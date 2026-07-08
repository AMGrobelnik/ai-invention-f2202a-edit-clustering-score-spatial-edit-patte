#!/usr/bin/env python3
"""ECS vs Jaccard Statistical Evaluation for near-duplicate detection."""

import json
import sys
import math
from pathlib import Path

import numpy as np
from loguru import logger
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
Path("logs").mkdir(exist_ok=True)
logger.add("logs/eval.log", rotation="30 MB", level="DEBUG")

WORKSPACE = Path("/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_2/gen_art/gen_art_evaluation_1")
METHOD_OUT = Path("/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_experiment_1/full_method_out.json")
B = 2000
RNG = np.random.default_rng(42)


def bootstrap_auc(scores: np.ndarray, labels: np.ndarray, b: int = B) -> tuple[float, float, float]:
    """Return (auc, ci_low, ci_high) via bootstrap."""
    n = len(labels)
    aucs = []
    for _ in range(b):
        idx = RNG.integers(0, n, size=n)
        sl, ll = scores[idx], labels[idx]
        if ll.sum() == 0 or ll.sum() == n:
            continue
        try:
            aucs.append(roc_auc_score(ll, sl))
        except Exception:
            continue
    aucs = np.array(aucs)
    return float(np.mean(aucs)), float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))


def bootstrap_delta_auc(scores1: np.ndarray, scores2: np.ndarray, labels: np.ndarray, b: int = B) -> tuple[float, float, float]:
    """Bootstrap CI for delta AUC = auc(scores1) - auc(scores2)."""
    n = len(labels)
    deltas = []
    for _ in range(b):
        idx = RNG.integers(0, n, size=n)
        sl1, sl2, ll = scores1[idx], scores2[idx], labels[idx]
        if ll.sum() == 0 or ll.sum() == n:
            continue
        try:
            d = roc_auc_score(ll, sl1) - roc_auc_score(ll, sl2)
            deltas.append(d)
        except Exception:
            continue
    deltas = np.array(deltas)
    return float(np.mean(deltas)), float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))


def cv_auc(X: np.ndarray, y: np.ndarray) -> float:
    """5-fold stratified CV AUC."""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs = []
    for tr, te in skf.split(X, y):
        clf = LogisticRegression(max_iter=1000)
        clf.fit(X[tr], y[tr])
        prob = clf.predict_proba(X[te])[:, 1]
        if y[te].sum() == 0 or y[te].sum() == len(y[te]):
            continue
        aucs.append(roc_auc_score(y[te], prob))
    return float(np.mean(aucs))


@logger.catch(reraise=True)
def main():
    logger.info(f"Loading method_out from {METHOD_OUT}")
    data = json.loads(METHOD_OUT.read_text())
    examples = data["datasets"][0]["examples"]
    logger.info(f"Loaded {len(examples)} examples")

    # Extract fields
    pair_types = [e["metadata_pair_type"] for e in examples]
    jaccards = np.array([float(e["metadata_jaccard"]) for e in examples])
    ecss = np.array([float(e["metadata_ecs"]) for e in examples])

    # Inverted ECS score: lower ECS = more near-dup, so use -ECS as score
    inv_ecs = -ecss

    # --- Indices ---
    nd_mask = np.array([p == "near_dup" for p in pair_types])
    hn_mask = np.array([p == "hard_neg" for p in pair_types])
    hard_mask = nd_mask | hn_mask
    hard_labels = nd_mask[hard_mask].astype(int)  # 1=near_dup, 0=hard_neg

    nd_idx = np.where(nd_mask)[0]
    hn_idx = np.where(hn_mask)[0]

    logger.info(f"near_dup={nd_mask.sum()} hard_neg={hn_mask.sum()} random={(~hard_mask).sum()}")
    logger.info(f"Hard subset size: {hard_mask.sum()} (nd={nd_mask.sum()}, hn={hn_mask.sum()})")

    # ========== METRIC 1: Inverted ECS AUC on hard subset ==========
    hard_inv_ecs = inv_ecs[hard_mask]
    hard_jaccard = jaccards[hard_mask]

    ecs_auc, ecs_ci_lo, ecs_ci_hi = bootstrap_auc(hard_inv_ecs, hard_labels)
    jac_auc_hard, jac_ci_lo, jac_ci_hi = bootstrap_auc(hard_jaccard, hard_labels)
    logger.info(f"[M1] Inverted-ECS AUC on hard subset: {ecs_auc:.4f} CI [{ecs_ci_lo:.4f},{ecs_ci_hi:.4f}]")
    logger.info(f"[M1] Jaccard AUC on hard subset: {jac_auc_hard:.4f} CI [{jac_ci_lo:.4f},{jac_ci_hi:.4f}]")

    # ========== METRIC 2: Delta AUC (jaccard5+inv_ECS) vs jaccard5 alone ==========
    # (a) Full dataset
    full_labels_3 = np.array([1 if p == "near_dup" else 0 for p in pair_types])
    # Use predict scores from method_out (trained scores)
    pred_jaccard = np.array([float(e["predict_jaccard"]) for e in examples])
    pred_ecs = np.array([float(e["predict_ecs"]) for e in examples])
    pred_combined = np.array([float(e["predict_combined"]) for e in examples])

    delta_full, d_full_lo, d_full_hi = bootstrap_delta_auc(pred_combined, pred_jaccard, full_labels_3)
    logger.info(f"[M2a] Delta AUC (combined vs jaccard) full: {delta_full:.4f} CI [{d_full_lo:.4f},{d_full_hi:.4f}]")

    # (b) Hard subset - use CV on hard subset with [jaccard, -ecs] vs jaccard alone
    X_hard = np.column_stack([hard_jaccard, hard_inv_ecs])
    X_jac_hard = hard_jaccard.reshape(-1, 1)

    if hard_labels.sum() > 0 and hard_labels.sum() < len(hard_labels) and len(hard_labels) >= 5:
        auc_combined_hard = cv_auc(X_hard, hard_labels)
        auc_jac_hard_cv = cv_auc(X_jac_hard, hard_labels)
    else:
        # Too few samples for 5-fold CV, use direct AUC
        clf_c = LogisticRegression(max_iter=1000).fit(X_hard, hard_labels)
        auc_combined_hard = roc_auc_score(hard_labels, clf_c.predict_proba(X_hard)[:, 1])
        clf_j = LogisticRegression(max_iter=1000).fit(X_jac_hard, hard_labels)
        auc_jac_hard_cv = roc_auc_score(hard_labels, clf_j.predict_proba(X_jac_hard)[:, 1])
        logger.warning("Hard subset too small for 5-fold CV; using in-sample AUC")

    # Bootstrap delta for hard subset using raw scores
    delta_hard, d_hard_lo, d_hard_hi = bootstrap_delta_auc(hard_inv_ecs, hard_jaccard, hard_labels)
    logger.info(f"[M2b] Delta AUC (inv_ECS vs jaccard) hard: {delta_hard:.4f} CI [{d_hard_lo:.4f},{d_hard_hi:.4f}]")
    logger.info(f"[M2b] Combined CV AUC on hard: {auc_combined_hard:.4f}, Jaccard CV AUC: {auc_jac_hard_cv:.4f}")

    # ========== METRIC 3: Dataset source labeling ==========
    source = "synthetic_vocab_template"
    logger.info(f"[M3] Dataset source: {source} (NOT Wikipedia-derived)")

    # ========== METRIC 4: Length-stratified AUC ==========
    # Estimate length from input string: "pair_type=X jaccard=Y ecs=Z"
    # We don't have actual word counts, so we derive proxy from ECS magnitude
    # ECS = var/mean of inter-edit-gap positions → larger document → more absolute gap values
    # Instead, use ECS as proxy (monotone with length) — bin hard subset by ECS range
    # Better: use rank-based tercile on hard subset ECS values
    hard_ecs_vals = ecss[hard_mask]
    tercile_bounds = np.percentile(hard_ecs_vals, [33.3, 66.7])
    tercile_labels_arr = np.digitize(hard_ecs_vals, tercile_bounds)  # 0, 1, 2

    length_strat = {}
    for t, name in enumerate(["short", "medium", "long"]):
        tmask = tercile_labels_arr == t
        if tmask.sum() < 2 or hard_labels[tmask].sum() == 0 or hard_labels[tmask].sum() == tmask.sum():
            length_strat[name] = {"n": int(tmask.sum()), "note": "insufficient_class_diversity"}
            continue
        ecs_t_auc, _, _ = bootstrap_auc(hard_inv_ecs[tmask], hard_labels[tmask])
        jac_t_auc, _, _ = bootstrap_auc(hard_jaccard[tmask], hard_labels[tmask])
        length_strat[name] = {
            "n": int(tmask.sum()),
            "inv_ecs_auc": float(ecs_t_auc),
            "jaccard_auc": float(jac_t_auc),
        }
    logger.info(f"[M4] Length-stratified AUC: {length_strat}")

    # ========== METRIC 5: Depth-2 Decision Tree ==========
    dt_result = {}
    if len(hard_labels) >= 4 and hard_labels.sum() > 0:
        X_tree = np.column_stack([hard_jaccard, hard_inv_ecs])
        dt = DecisionTreeClassifier(max_depth=2, random_state=42)
        dt.fit(X_tree, hard_labels)
        tree = dt.tree_
        dt_result = {
            "feature_names": ["jaccard", "inv_ecs"],
            "n_nodes": int(tree.node_count),
            "root_feature": int(tree.feature[0]),
            "root_threshold": float(tree.threshold[0]),
            "root_impurity": float(tree.impurity[0]),
            "feature_importances": {
                "jaccard": float(dt.feature_importances_[0]),
                "inv_ecs": float(dt.feature_importances_[1]),
            },
        }
        # Extract child splits if they exist
        left_child = tree.children_left[0]
        right_child = tree.children_right[0]
        if left_child != -1:
            dt_result["left_split"] = {
                "feature": int(tree.feature[left_child]),
                "threshold": float(tree.threshold[left_child]),
            }
        if right_child != -1:
            dt_result["right_split"] = {
                "feature": int(tree.feature[right_child]),
                "threshold": float(tree.threshold[right_child]),
            }
    logger.info(f"[M5] Decision tree: {dt_result}")

    # ========== METRIC 6: Mann-Whitney U statistics ==========
    nd_ecs = ecss[nd_mask]
    hn_ecs = ecss[hn_mask]

    mw_stat, mw_p = stats.mannwhitneyu(nd_ecs, hn_ecs, alternative="two-sided")
    # MW with correct direction: nd should have LOWER ecs
    mw_stat_less, mw_p_less = stats.mannwhitneyu(nd_ecs, hn_ecs, alternative="less")

    median_nd = float(np.median(nd_ecs))
    median_hn = float(np.median(hn_ecs))
    median_ratio = float(median_nd / median_hn) if median_hn > 0 else float("nan")

    # Cohen's d on log-IoD
    log_nd = np.log(nd_ecs + 1)
    log_hn = np.log(hn_ecs + 1)
    pooled_std = math.sqrt((log_nd.var() + log_hn.var()) / 2)
    cohens_d = float((log_nd.mean() - log_hn.mean()) / pooled_std) if pooled_std > 0 else 0.0

    logger.info(f"[M6] MW U={mw_stat:.1f} p={mw_p:.6f} (two-sided), p_less={mw_p_less:.6f}")
    logger.info(f"[M6] Median IoD near_dup={median_nd:.3f}, hard_neg={median_hn:.3f}, ratio={median_ratio:.3f}")
    logger.info(f"[M6] Cohen's d on log-IoD={cohens_d:.3f}")

    # ========== METRIC 2 supplemental: Boilerplate augmented hard subset ==========
    # Simulate: hard_neg jaccard += 0.35 (boilerplate overlap), near_dup unchanged
    jac_bpl = hard_jaccard.copy()
    jac_bpl[hard_labels == 0] = np.minimum(1.0, jac_bpl[hard_labels == 0] + 0.35)
    # ECS unchanged (boilerplate doesn't cluster edits)
    bpl_inv_ecs = hard_inv_ecs.copy()

    bpl_ecs_auc, bpl_ecs_ci_lo, bpl_ecs_ci_hi = bootstrap_auc(bpl_inv_ecs, hard_labels)
    bpl_jac_auc, bpl_jac_ci_lo, bpl_jac_ci_hi = bootstrap_auc(jac_bpl, hard_labels)
    bpl_delta, bpl_d_lo, bpl_d_hi = bootstrap_delta_auc(bpl_inv_ecs, jac_bpl, hard_labels)
    logger.info(f"[M2-BPL] Boilerplate-augmented: ECS AUC={bpl_ecs_auc:.4f}, Jaccard AUC={bpl_jac_auc:.4f}, delta={bpl_delta:.4f}")

    # ========== METRIC 7: Verdict ==========
    ecs_auc_ok = ecs_auc > 0.65
    delta_hard_ok = delta_hard > 0.03
    jaccard_ceiling = jac_auc_hard >= 0.999

    if ecs_auc_ok and delta_hard_ok:
        verdict = "CONFIRMED"
    elif ecs_auc_ok or delta_hard_ok:
        verdict = "PARTIAL"
    else:
        verdict = "DISCONFIRMED"

    logger.info(f"[M7] Verdict: {verdict} (ecs_auc_ok={ecs_auc_ok}, delta_hard_ok={delta_hard_ok}, jaccard_ceiling={jaccard_ceiling})")

    # ========== Build output JSON ==========
    metrics_agg = {
        "inv_ecs_auc_hard": float(ecs_auc),
        "inv_ecs_auc_hard_ci_lo": float(ecs_ci_lo),
        "inv_ecs_auc_hard_ci_hi": float(ecs_ci_hi),
        "jaccard_auc_hard": float(jac_auc_hard),
        "jaccard_auc_hard_ci_lo": float(jac_ci_lo),
        "jaccard_auc_hard_ci_hi": float(jac_ci_hi),
        "delta_auc_full_combined_vs_jaccard": float(delta_full),
        "delta_auc_full_ci_lo": float(d_full_lo),
        "delta_auc_full_ci_hi": float(d_full_hi),
        "delta_auc_hard_inv_ecs_vs_jaccard": float(delta_hard),
        "delta_auc_hard_ci_lo": float(d_hard_lo),
        "delta_auc_hard_ci_hi": float(d_hard_hi),
        "bpl_inv_ecs_auc": float(bpl_ecs_auc),
        "bpl_jaccard_auc": float(bpl_jac_auc),
        "bpl_delta_auc": float(bpl_delta),
        "bpl_delta_ci_lo": float(bpl_d_lo),
        "bpl_delta_ci_hi": float(bpl_d_hi),
        "mw_u_statistic": float(mw_stat),
        "mw_p_value_two_sided": float(mw_p),
        "mw_p_value_less": float(mw_p_less),
        "median_iod_near_dup": float(median_nd),
        "median_iod_hard_neg": float(median_hn),
        "median_iod_ratio": float(median_ratio),
        "cohens_d_log_iod": float(cohens_d),
        "n_near_dup": int(nd_mask.sum()),
        "n_hard_neg": int(hn_mask.sum()),
        "jaccard_ceiling_on_hard": float(1 if jaccard_ceiling else 0),
        "verdict_confirmed": float(1 if verdict == "CONFIRMED" else 0),
        "verdict_partial": float(1 if verdict == "PARTIAL" else 0),
        "verdict_disconfirmed": float(1 if verdict == "DISCONFIRMED" else 0),
    }

    # Per-example eval rows
    eval_examples = []
    for i, e in enumerate(examples):
        jac = float(e["metadata_jaccard"])
        ecs = float(e["metadata_ecs"])
        pt = e["metadata_pair_type"]
        label_int = 1 if pt == "near_dup" else 0
        is_hard = 1 if pt in ("near_dup", "hard_neg") else 0
        eval_examples.append({
            "input": e["input"],
            "output": e["output"],
            "predict_jaccard": e["predict_jaccard"],
            "predict_ecs": e["predict_ecs"],
            "predict_combined": e["predict_combined"],
            "predict_all_features": e["predict_all_features"],
            "metadata_pair_type": pt,
            "metadata_jaccard": e["metadata_jaccard"],
            "metadata_ecs": e["metadata_ecs"],
            "metadata_inv_ecs": str(round(-ecs, 4)),
            "metadata_source": source,
            "metadata_is_hard_subset": str(is_hard),
            "eval_label": float(label_int),
            "eval_inv_ecs": float(-ecs),
            "eval_correct_jaccard": float(1 if (jac > 0.1) == (pt == "near_dup") else 0),
        })

    eval_out = {
        "metadata": {
            "evaluation": "ECS vs Jaccard Statistical Evaluation",
            "source": source,
            "source_note": "All pairs generated from synthetic vocabulary-template articles (NOT Wikipedia-derived). Each article uses a 60-word topic-specific vocabulary (politics/sports/science/business/technology). Claims verified on synthetic data only.",
            "n_pairs": len(examples),
            "n_near_dup": int(nd_mask.sum()),
            "n_hard_neg": int(hn_mask.sum()),
            "n_random": int((~hard_mask).sum()),
            "verdict": verdict,
            "jaccard_ceiling_note": "Jaccard AUC=1.0 on hard subset blocks complementarity measurement (all hard_neg have Jaccard=0.0)",
            "boilerplate_augmentation": "Simulated: hard_neg jaccard += 0.35 (shared prefix), near_dup unchanged; ECS unchanged",
            "decision_tree": dt_result,
            "length_stratification_note": "Length proxy = ECS magnitude (no raw word counts in method_out); binned hard subset by ECS tercile",
            "length_stratified_auc": length_strat,
            "mw_details": {
                "statistic": float(mw_stat),
                "p_two_sided": float(mw_p),
                "p_less": float(mw_p_less),
                "median_nd": float(median_nd),
                "median_hn": float(median_hn),
                "ratio": float(median_ratio),
                "cohens_d_log_iod": float(cohens_d),
            },
            "delta_auc_threshold": 0.03,
            "ecs_auc_threshold": 0.65,
        },
        "metrics_agg": metrics_agg,
        "datasets": [
            {
                "dataset": "wikipedia_near_dup_synthetic_eval",
                "examples": eval_examples,
            }
        ],
    }

    out_path = WORKSPACE / "eval_out.json"
    out_path.write_text(json.dumps(eval_out, indent=2))
    logger.info(f"Wrote {out_path}")

    logger.info(f"\n{'='*60}")
    logger.info(f"VERDICT: {verdict}")
    logger.info(f"  Inverted-ECS AUC on hard subset: {ecs_auc:.4f} (>{0.65}? {ecs_auc_ok})")
    logger.info(f"  Delta AUC (inv_ECS-jaccard) hard: {delta_hard:.4f} (>0.03? {delta_hard_ok})")
    logger.info(f"  Jaccard ceiling: {jaccard_ceiling}")
    logger.info(f"  MW p (nd<hn ECS): {mw_p_less:.4f}")
    logger.info(f"  Hard_neg n={int(hn_mask.sum())} (NOTE: very small, statistical power limited)")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
