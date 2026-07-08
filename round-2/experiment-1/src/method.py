#!/usr/bin/env python3
"""ECS vs Jaccard near-duplicate detection experiment on Wiki + Boilerplate benchmarks."""

import json
import math
import os
import re
import resource
import sys
import time
import gc
from pathlib import Path
from typing import Any

import difflib
import numpy as np
import pandas as pd
import requests
import scipy.stats as stats
from loguru import logger
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

# ── Logging ──────────────────────────────────────────────────────────────────
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
Path("logs").mkdir(exist_ok=True)
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

# ── Resource limits ───────────────────────────────────────────────────────────
RAM_LIMIT = 20 * 1024**3  # 20 GB (container has 29 GB)
resource.setrlimit(resource.RLIMIT_AS, (RAM_LIMIT * 3, RAM_LIMIT * 3))

# ── Paths ─────────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).parent
DEP_DIR = Path("/ai-inventor/aii_data/runs/run_E1yko-FJ_C_D/3_invention_loop/iter_1/gen_art/gen_art_dataset_1")
FULL_DATA = DEP_DIR / "full_data_out.json"
OUTPUT = WORKSPACE / "method_out.json"

# Fixed boilerplate text (~180 words)
BOILERPLATE = (
    "This article is provided under the Creative Commons Attribution-ShareAlike License. "
    "All content is for informational purposes only. Last updated: January 2024. "
    "Reproduction permitted with attribution. The views expressed do not represent any organization. "
    "See terms at creativecommons.org licenses by-sa 3.0 for full details on usage rights. "
    "Content may be freely shared modified and built upon under the same license terms provided "
    "that attribution is given to the original authors and contributors. This notice must be "
    "preserved in all derived works. Wikipedia contributors are the source of the underlying text. "
    "The Wikimedia Foundation does not endorse any particular use of this material. "
    "For educational and research purposes only. No warranties are provided regarding accuracy. "
    "Verify all facts independently before relying on this content for any purpose. "
    "This document was automatically generated and may contain errors or omissions. "
    "Contact the original source for authoritative information. End of legal notice. "
)


# ── Feature extraction ────────────────────────────────────────────────────────

def tokenize(text: str) -> list[str]:
    return re.findall(r'\b\w+\b', text.lower())


def jaccard_ngram(a_tokens: list[str], b_tokens: list[str], n: int) -> float:
    a_sh = set(zip(*[a_tokens[i:] for i in range(n)]))
    b_sh = set(zip(*[b_tokens[i:] for i in range(n)]))
    if not a_sh and not b_sh:
        return 0.0
    return len(a_sh & b_sh) / len(a_sh | b_sh)


def compute_ecs(a_tokens: list[str], b_tokens: list[str]) -> dict[str, float]:
    """Index of Dispersion (IoD) of edit positions → ECS. Low IoD = clustered edits = near-dup."""
    matcher = difflib.SequenceMatcher(None, a_tokens, b_tokens, autojunk=False)
    opcodes = matcher.get_opcodes()

    total_len = max(len(a_tokens), 1)
    edit_pos_raw = [op[1] for op in opcodes if op[0] != 'equal']

    gaps = [edit_pos_raw[i + 1] - edit_pos_raw[i] for i in range(len(edit_pos_raw) - 1)]

    if len(gaps) < 2:
        iod = 0.0
    else:
        mu = float(np.mean(gaps))
        var = float(np.var(gaps))
        iod = var / mu if mu > 0 else 0.0

    inv_ecs = 1.0 / (1.0 + iod)

    equal_lengths = [op[4] - op[3] for op in opcodes if op[0] == 'equal']
    longest_run = max(equal_lengths) if equal_lengths else 0
    longest_run_frac = longest_run / total_len

    n_edit_ops = sum(1 for op in opcodes if op[0] != 'equal')
    edit_count_norm = n_edit_ops / (len(a_tokens) + len(b_tokens) + 1)

    return {
        'ecs': iod,
        'inv_ecs': inv_ecs,
        'longest_run_frac': longest_run_frac,
        'edit_count_norm': edit_count_norm,
        'n_edit_positions': len(edit_pos_raw),
    }


def extract_features(row: dict) -> dict:
    inp = row['input']
    if isinstance(inp, str):
        inp = json.loads(inp)
    ta, tb = inp['text_a'], inp['text_b']
    ta_tok, tb_tok = tokenize(ta), tokenize(tb)
    j5 = jaccard_ngram(ta_tok, tb_tok, 5)
    j2 = jaccard_ngram(ta_tok, tb_tok, 2)
    ecs_feats = compute_ecs(ta_tok, tb_tok)
    return {
        'jaccard_5gram': j5,
        'jaccard_2gram': j2,
        **ecs_feats,
        'label': row['output'],
        'fold': row.get('metadata_fold', row.get('fold', 0)),
    }


# ── Boilerplate benchmark construction ───────────────────────────────────────

def build_boilerplate_benchmark(wiki_rows: list[dict]) -> list[dict]:
    """Build 900-pair boilerplate-hard-neg benchmark reusing wiki articles."""
    logger.info("Building boilerplate benchmark from existing wiki articles...")

    # Group articles by category (use text_a from existing rows)
    by_category: dict[str, list[str]] = {}
    for row in wiki_rows:
        inp = json.loads(row['input']) if isinstance(row['input'], str) else row['input']
        cat = row.get('metadata_category', 'unknown')
        if cat not in by_category:
            by_category[cat] = []
        # store text_a
        by_category[cat].append(inp['text_a'])

    logger.info(f"Categories: {list(by_category.keys())}")

    # Near-duplicate pairs: same as wiki (reuse near_dup rows)
    nd_rows = [r for r in wiki_rows if r['output'] == 'near_duplicate']
    hard_neg_rows = [r for r in wiki_rows if r['output'] == 'hard_negative']
    random_rows = [r for r in wiki_rows if r['output'] == 'random']

    boilerplate_rows = []
    fold = 0

    # Class 1: Near-duplicates (same as wiki dataset — splice edited pairs)
    for i, row in enumerate(nd_rows[:300]):
        inp = json.loads(row['input']) if isinstance(row['input'], str) else row['input']
        boilerplate_rows.append({
            'input': json.dumps({'text_a': inp['text_a'], 'text_b': inp['text_b']}),
            'output': 'near_duplicate',
            'metadata_fold': i % 5,
        })

    # Class 2: Boilerplate-hard-negatives (different articles same category + shared boilerplate prefix)
    boilerplate_count = 0
    same_cat_pairs: list[tuple[str, str]] = []

    # Build same-category pairs from hard_negative rows (both texts in same category)
    for row in hard_neg_rows:
        inp = json.loads(row['input']) if isinstance(row['input'], str) else row['input']
        ta = BOILERPLATE + inp['text_a']
        tb = BOILERPLATE + inp['text_b']
        # Verify Jaccard is inflated
        tok_a = tokenize(ta)
        tok_b = tokenize(tb)
        j5 = jaccard_ngram(tok_a, tok_b, 5)
        same_cat_pairs.append((ta, tb, j5))

    # Also build cross-category pairs with boilerplate to fill up
    logger.info(f"Same-cat pairs with boilerplate: {len(same_cat_pairs)}, mean J5={np.mean([x[2] for x in same_cat_pairs]):.3f}")

    # Take up to 300 boilerplate-hard-neg pairs
    for i, (ta, tb, j5) in enumerate(same_cat_pairs[:300]):
        boilerplate_rows.append({
            'input': json.dumps({'text_a': ta, 'text_b': tb}),
            'output': 'boilerplate_hard_negative',
            'metadata_fold': i % 5,
            'metadata_jaccard_5gram': j5,
        })

    # Class 3: Random pairs (different categories, no boilerplate)
    for i, row in enumerate(random_rows[:300]):
        inp = json.loads(row['input']) if isinstance(row['input'], str) else row['input']
        boilerplate_rows.append({
            'input': json.dumps({'text_a': inp['text_a'], 'text_b': inp['text_b']}),
            'output': 'random',
            'metadata_fold': i % 5,
        })

    logger.info(f"Boilerplate benchmark: {len(boilerplate_rows)} rows")
    class_counts = {}
    for r in boilerplate_rows:
        class_counts[r['output']] = class_counts.get(r['output'], 0) + 1
    logger.info(f"Class distribution: {class_counts}")

    # Print J5 histogram for boilerplate class
    bp_j5 = [r.get('metadata_jaccard_5gram', 0) for r in boilerplate_rows if r['output'] == 'boilerplate_hard_negative']
    if bp_j5:
        logger.info(f"Boilerplate J5 range: [{min(bp_j5):.3f}, {max(bp_j5):.3f}], mean={np.mean(bp_j5):.3f}")

    return boilerplate_rows


# ── CV Evaluation ─────────────────────────────────────────────────────────────

FEATURE_SETS = {
    'jaccard5_only': ['jaccard_5gram'],
    'jaccard2_only': ['jaccard_2gram'],
    'inv_ecs_only': ['inv_ecs'],
    'jaccard5_inv_ecs': ['jaccard_5gram', 'inv_ecs'],
    'jaccard2_inv_ecs': ['jaccard_2gram', 'inv_ecs'],
    'all_features': ['jaccard_5gram', 'jaccard_2gram', 'inv_ecs', 'longest_run_frac', 'edit_count_norm'],
}


def run_cv(features_list: list[dict], feature_sets: dict, label_map: dict) -> dict:
    df = pd.DataFrame(features_list)
    df['y'] = df['label'].map(label_map)
    df = df.dropna(subset=['y'])

    results = {}
    for fs_name, cols in feature_sets.items():
        fold_aucs = []
        for fold_id in range(5):
            train = df[df['fold'] != fold_id]
            test = df[df['fold'] == fold_id]
            if len(test) == 0 or len(test['y'].unique()) < 2:
                continue

            X_train = train[cols].fillna(0).values
            X_test = test[cols].fillna(0).values
            y_train = train['y'].values
            y_test = test['y'].values

            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            clf = LogisticRegression(max_iter=1000, C=1.0)
            clf.fit(X_train, y_train)
            probs = clf.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, probs)
            fold_aucs.append(auc)

        results[fs_name] = {
            'auc_mean': float(np.mean(fold_aucs)) if fold_aucs else 0.0,
            'auc_std': float(np.std(fold_aucs)) if fold_aucs else 0.0,
            'fold_aucs': [float(x) for x in fold_aucs],
        }
    return results


def bootstrap_delta_auc(features_list: list[dict], col_a: list[str], col_b: list[str],
                         label_map: dict, B: int = 2000) -> dict:
    df = pd.DataFrame(features_list)
    df['y'] = df['label'].map(label_map)
    df = df.dropna(subset=['y'])
    if len(df['y'].unique()) < 2:
        return {'mean': 0.0, 'ci_lo': 0.0, 'ci_hi': 0.0}

    rng = np.random.default_rng(42)
    deltas = []
    for _ in range(B):
        idx = rng.integers(0, len(df), size=len(df))
        sample = df.iloc[idx]
        Xa = sample[col_a].fillna(0).values
        Xb = sample[col_b].fillna(0).values
        y = sample['y'].values
        if len(np.unique(y)) < 2:
            continue

        sc_a = StandardScaler()
        sc_b = StandardScaler()
        clf_a = LogisticRegression(max_iter=500).fit(sc_a.fit_transform(Xa), y)
        clf_b = LogisticRegression(max_iter=500).fit(sc_b.fit_transform(Xb), y)

        auc_a = roc_auc_score(y, clf_a.predict_proba(sc_a.transform(Xa))[:, 1])
        auc_b = roc_auc_score(y, clf_b.predict_proba(sc_b.transform(Xb))[:, 1])
        deltas.append(auc_b - auc_a)

    deltas = np.array(deltas)
    return {
        'mean': float(np.mean(deltas)),
        'ci_lo': float(np.percentile(deltas, 2.5)),
        'ci_hi': float(np.percentile(deltas, 97.5)),
    }


def mann_whitney_iod(features_list: list[dict], neg_label: str = 'hard_negative') -> dict:
    df = pd.DataFrame(features_list)
    nd = df[df['label'] == 'near_duplicate']['ecs'].dropna()
    hn = df[df['label'] == neg_label]['ecs'].dropna()
    if len(nd) == 0 or len(hn) == 0:
        return {'error': 'insufficient data'}
    u, p = stats.mannwhitneyu(nd, hn, alternative='less')
    return {
        'median_iod_near_dup': float(nd.median()),
        'median_iod_hard_neg': float(hn.median()),
        'mann_whitney_p': float(p),
        'n_near_dup': int(len(nd)),
        'n_hard_neg': int(len(hn)),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

@logger.catch(reraise=True)
def main():
    t0 = time.time()

    # ── Load wiki dataset ──────────────────────────────────────────────────
    logger.info(f"Loading wiki dataset from {FULL_DATA}")
    raw = json.loads(FULL_DATA.read_text())
    wiki_rows = raw['datasets'][0]['examples']
    logger.info(f"Loaded {len(wiki_rows)} wiki rows")

    # ── MINI TEST first (60 rows) ──────────────────────────────────────────
    logger.info("=== MINI TEST (60 rows) ===")
    mini = wiki_rows[:60]
    mini_feats = [extract_features(r) for r in mini]
    nd_iod = [f['ecs'] for f in mini_feats if f['label'] == 'near_duplicate']
    hn_iod = [f['ecs'] for f in mini_feats if f['label'] == 'hard_negative']
    logger.info(f"Mini: near_dup IoD median={np.median(nd_iod):.3f}, hard_neg IoD median={np.median(hn_iod):.3f}")
    # Validate features
    for feat in mini_feats[:3]:
        logger.info(f"Sample: j5={feat['jaccard_5gram']:.3f} j2={feat['jaccard_2gram']:.3f} inv_ecs={feat['inv_ecs']:.3f} longest_run={feat['longest_run_frac']:.3f} label={feat['label']}")
    assert all(0 <= f['jaccard_5gram'] <= 1 for f in mini_feats), "j5 out of range"
    assert all(0 < f['inv_ecs'] <= 1 for f in mini_feats), "inv_ecs out of range"
    logger.info("Mini test PASSED")

    # ── Extract features for full wiki dataset ─────────────────────────────
    logger.info("Extracting features for all 900 wiki pairs...")
    wiki_feats = [extract_features(r) for r in wiki_rows]
    logger.info(f"Done. {len(wiki_feats)} feature rows")

    # ── Build boilerplate benchmark ────────────────────────────────────────
    bp_rows = build_boilerplate_benchmark(wiki_rows)
    logger.info("Extracting features for boilerplate benchmark...")
    bp_feats = [extract_features(r) for r in bp_rows]
    logger.info(f"Done. {len(bp_feats)} boilerplate feature rows")

    # ── Evaluate: near_dup vs hard_neg ────────────────────────────────────
    label_map_hard = {'near_duplicate': 1, 'hard_negative': 0, 'boilerplate_hard_negative': 0}
    label_map_all = {'near_duplicate': 1, 'hard_negative': 0, 'boilerplate_hard_negative': 0, 'random': 0}

    logger.info("Running 5-fold CV on wiki benchmark (hard subset)...")
    wiki_cv_hard = run_cv(wiki_feats, FEATURE_SETS, label_map_hard)
    for fs, res in wiki_cv_hard.items():
        logger.info(f"  wiki hard | {fs}: AUC={res['auc_mean']:.3f}±{res['auc_std']:.3f}")

    logger.info("Running 5-fold CV on wiki benchmark (all labels)...")
    wiki_cv_all = run_cv(wiki_feats, FEATURE_SETS, label_map_all)

    logger.info("Running 5-fold CV on boilerplate benchmark (hard subset)...")
    bp_cv_hard = run_cv(bp_feats, FEATURE_SETS, label_map_hard)
    for fs, res in bp_cv_hard.items():
        logger.info(f"  bp hard   | {fs}: AUC={res['auc_mean']:.3f}±{res['auc_std']:.3f}")

    logger.info("Running 5-fold CV on boilerplate benchmark (all labels)...")
    bp_cv_all = run_cv(bp_feats, FEATURE_SETS, label_map_all)

    # ── Bootstrap CI for key delta ─────────────────────────────────────────
    logger.info("Bootstrap CI for Jaccard2+invECS vs Jaccard2 alone on boilerplate (B=2000)...")
    delta_bp = bootstrap_delta_auc(
        bp_feats,
        col_a=['jaccard_2gram'],
        col_b=['jaccard_2gram', 'inv_ecs'],
        label_map=label_map_hard,
        B=2000,
    )
    logger.info(f"Delta AUC (J2+invECS vs J2): mean={delta_bp['mean']:.3f} CI=[{delta_bp['ci_lo']:.3f},{delta_bp['ci_hi']:.3f}]")

    # Also compute for wiki
    logger.info("Bootstrap CI for Jaccard2+invECS vs Jaccard2 alone on wiki (B=2000)...")
    delta_wiki = bootstrap_delta_auc(
        wiki_feats,
        col_a=['jaccard_2gram'],
        col_b=['jaccard_2gram', 'inv_ecs'],
        label_map=label_map_hard,
        B=2000,
    )
    logger.info(f"Delta AUC (J2+invECS vs J2) wiki: mean={delta_wiki['mean']:.3f} CI=[{delta_wiki['ci_lo']:.3f},{delta_wiki['ci_hi']:.3f}]")

    # ── Mann-Whitney IoD ──────────────────────────────────────────────────
    wiki_mw = mann_whitney_iod(wiki_feats, neg_label='hard_negative')
    bp_mw = mann_whitney_iod(bp_feats, neg_label='boilerplate_hard_negative')
    logger.info(f"Wiki MW: near_dup IoD median={wiki_mw['median_iod_near_dup']:.3f}, hard_neg={wiki_mw['median_iod_hard_neg']:.3f}, p={wiki_mw['mann_whitney_p']:.4f}")
    logger.info(f"BP MW:   near_dup IoD median={bp_mw['median_iod_near_dup']:.3f}, bp_hard_neg={bp_mw['median_iod_hard_neg']:.3f}, p={bp_mw['mann_whitney_p']:.4f}")

    # ── Key findings ───────────────────────────────────────────────────────
    bp_j2_auc = bp_cv_hard['jaccard2_only']['auc_mean']
    bp_j2_ecs_auc = bp_cv_hard['jaccard2_inv_ecs']['auc_mean']
    wiki_j2_auc = wiki_cv_hard['jaccard2_only']['auc_mean']
    wiki_j2_ecs_auc = wiki_cv_hard['jaccard2_inv_ecs']['auc_mean']
    hypothesis_confirmed = (bp_j2_ecs_auc - bp_j2_auc) >= 0.03

    logger.info(f"Hypothesis confirmed (delta>=0.03 on boilerplate): {hypothesis_confirmed}")
    logger.info(f"  BP: J2={bp_j2_auc:.3f}, J2+ECS={bp_j2_ecs_auc:.3f}, delta={bp_j2_ecs_auc-bp_j2_auc:.3f}")
    logger.info(f"  Wiki: J2={wiki_j2_auc:.3f}, J2+ECS={wiki_j2_ecs_auc:.3f}, delta={wiki_j2_ecs_auc-wiki_j2_auc:.3f}")

    # ── Per-pair predictions for schema compliance ─────────────────────────
    # Train on full data (no CV), get scores for each pair as predict_* fields
    def make_predictions(feats_list: list[dict], label_map: dict) -> list[dict]:
        """Return per-row predictions from each feature set using leave-one-fold-out."""
        df = pd.DataFrame(feats_list)
        df['y'] = df['label'].map(label_map).fillna(-1)

        # Predict scores via 5-fold: train on 4 folds, predict the held-out fold
        pred_cols = {}
        for fs_name, cols in FEATURE_SETS.items():
            scores = np.full(len(df), np.nan)
            for fold_id in range(5):
                tr_mask = df['fold'] != fold_id
                te_mask = df['fold'] == fold_id
                tr = df[tr_mask]
                te = df[te_mask]
                # use only labeled rows for training
                tr_lab = tr[tr['y'] >= 0]
                if len(tr_lab['y'].unique()) < 2 or len(te) == 0:
                    continue
                X_tr = tr_lab[cols].fillna(0).values
                y_tr = tr_lab['y'].values
                X_te = te[cols].fillna(0).values
                sc = StandardScaler()
                clf = LogisticRegression(max_iter=1000, C=1.0)
                clf.fit(sc.fit_transform(X_tr), y_tr)
                probs = clf.predict_proba(sc.transform(X_te))[:, 1]
                scores[te_mask.values] = probs
            pred_cols[fs_name] = scores
        return pred_cols

    logger.info("Generating per-pair predictions for wiki benchmark...")
    label_map_hard_wiki = {'near_duplicate': 1, 'hard_negative': 0}
    wiki_preds = make_predictions(wiki_feats, label_map_hard_wiki)

    logger.info("Generating per-pair predictions for boilerplate benchmark...")
    label_map_hard_bp = {'near_duplicate': 1, 'boilerplate_hard_negative': 0}
    bp_preds = make_predictions(bp_feats, label_map_hard_bp)

    # ── Build examples lists ────────────────────────────────────────────────
    def build_examples(feats_list, raw_rows, preds_dict, label_map):
        examples = []
        for i, (feat, row) in enumerate(zip(feats_list, raw_rows)):
            inp = row['input'] if isinstance(row['input'], str) else json.dumps(row['input'])
            label = feat['label']
            # binary output label for this task
            y_val = label_map.get(label)
            out_str = 'near_duplicate' if y_val == 1 else ('negative' if y_val == 0 else 'excluded')
            ex = {
                'input': inp,
                'output': out_str,
                'metadata_label': label,
                'metadata_fold': int(feat['fold']),
                'metadata_jaccard_5gram': round(float(feat['jaccard_5gram']), 4),
                'metadata_jaccard_2gram': round(float(feat['jaccard_2gram']), 4),
                'metadata_inv_ecs': round(float(feat['inv_ecs']), 4),
                'metadata_ecs_iod': round(float(feat['ecs']), 4),
                'metadata_longest_run_frac': round(float(feat['longest_run_frac']), 4),
                'metadata_edit_count_norm': round(float(feat['edit_count_norm']), 6),
            }
            for fs_name, scores in preds_dict.items():
                score = scores[i]
                ex[f'predict_{fs_name}'] = str(round(float(score), 4)) if not np.isnan(score) else 'NA'
            examples.append(ex)
        return examples

    wiki_examples = build_examples(wiki_feats, wiki_rows, wiki_preds, label_map_hard_wiki)
    bp_examples = build_examples(bp_feats, bp_rows, bp_preds, label_map_hard_bp)

    logger.info(f"Wiki examples: {len(wiki_examples)}, BP examples: {len(bp_examples)}")

    # ── Summary metrics ─────────────────────────────────────────────────────
    summary = {
        'wiki_benchmark': {
            'cv_results_hard_subset': wiki_cv_hard,
            'cv_results_all_labels': wiki_cv_all,
            'mann_whitney_iod': wiki_mw,
            'delta_auc_j2_plus_inv_ecs_vs_j2': delta_wiki,
        },
        'boilerplate_benchmark': {
            'cv_results_hard_subset': bp_cv_hard,
            'cv_results_all_labels': bp_cv_all,
            'mann_whitney_iod': bp_mw,
            'delta_auc_j2_plus_inv_ecs_vs_j2': delta_bp,
        },
        'key_findings': {
            'inv_ecs_auc_wiki_hard': wiki_cv_hard['inv_ecs_only']['auc_mean'],
            'inv_ecs_auc_boilerplate_hard': bp_cv_hard['inv_ecs_only']['auc_mean'],
            'wiki_j2_auc': wiki_j2_auc,
            'wiki_j2_plus_ecs_auc': wiki_j2_ecs_auc,
            'bp_j2_auc': bp_j2_auc,
            'bp_j2_plus_ecs_auc': bp_j2_ecs_auc,
            'delta_auc_boilerplate_mean': delta_bp['mean'],
            'delta_auc_boilerplate_ci_lo': delta_bp['ci_lo'],
            'delta_auc_boilerplate_ci_hi': delta_bp['ci_hi'],
            'hypothesis_confirmed': hypothesis_confirmed,
            'wiki_mw_p': wiki_mw['mann_whitney_p'],
            'bp_mw_p': bp_mw['mann_whitney_p'],
        },
    }

    # exp_gen_sol_out schema: {datasets: [{dataset, examples: [{input, output, metadata_*, predict_*}]}]}
    method_out = {
        'metadata': {
            'method_name': 'ECS vs Jaccard near-duplicate detection',
            'description': 'Edit Clustering Score (inverted IoD) vs n-gram Jaccard on Wiki + Boilerplate benchmarks',
            'hypothesis': 'inverted_ECS complements Jaccard when boilerplate inflates n-gram overlap',
            'runtime_seconds': round(time.time() - t0, 1),
            'summary': summary,
        },
        'datasets': [
            {
                'dataset': 'wiki_benchmark',
                'examples': wiki_examples,
            },
            {
                'dataset': 'boilerplate_benchmark',
                'examples': bp_examples,
            },
        ],
    }

    OUTPUT.write_text(json.dumps(method_out, indent=2))
    logger.info(f"Saved method_out.json ({OUTPUT.stat().st_size/1024:.1f} KB)")

    # Also save full results separately for paper writing convenience
    (WORKSPACE / "full_results.json").write_text(json.dumps(summary, indent=2))
    logger.info(f"Saved full_results.json")
    logger.info(f"Total runtime: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
