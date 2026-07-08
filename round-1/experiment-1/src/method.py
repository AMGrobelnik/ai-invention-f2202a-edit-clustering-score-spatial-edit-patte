#!/usr/bin/env python3
"""
Edit Clustering Score (ECS) vs Jaccard for Near-Duplicate Text Detection.

ECS = Index of Dispersion (variance/mean) of inter-edit-gap lengths from word-level LCS diff.
Hypothesis: ECS adds signal over Jaccard-only for near-duplicate detection because
localized edits (spliced sections) create clustered edit positions (high IoD),
whereas random/hard-negative pairs have scattered edits (low IoD).
"""

import difflib
import gc
import json
import math
import multiprocessing as mp
import os
import random
import resource
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from scipy.stats import mannwhitneyu
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ── Logging ──────────────────────────────────────────────────────────────────
WS = Path(__file__).parent
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs/run.log", rotation="30 MB", level="DEBUG")

# ── Hardware & Memory limits ──────────────────────────────────────────────────
def _detect_cpus() -> int:
    try:
        parts = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        if parts[0] != "max":
            return math.ceil(int(parts[0]) / int(parts[1]))
    except (FileNotFoundError, ValueError):
        pass
    try:
        q = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text())
        p = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text())
        if q > 0:
            return math.ceil(q / p)
    except (FileNotFoundError, ValueError):
        pass
    try:
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        pass
    return os.cpu_count() or 1


def _container_ram_gb() -> float:
    for p in ["/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory/memory.limit_in_bytes"]:
        try:
            v = Path(p).read_text().strip()
            if v != "max" and int(v) < 1_000_000_000_000:
                return int(v) / 1e9
        except (FileNotFoundError, ValueError):
            pass
    import psutil
    return psutil.virtual_memory().total / 1e9


NUM_CPUS = _detect_cpus()
TOTAL_RAM_GB = _container_ram_gb()
RAM_BUDGET = int(min(TOTAL_RAM_GB * 0.6, 16) * 1024**3)
resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET * 3, RAM_BUDGET * 3))
logger.info(f"Hardware: {NUM_CPUS} CPUs, {TOTAL_RAM_GB:.1f}GB RAM, budget={RAM_BUDGET/1e9:.1f}GB")

# ── Config ────────────────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_ARTICLES = 3000
PAIRS_PER_CLASS = 300
MAX_IOD_CLIP = 200.0
MIN_WORDS = 100
MAX_WORDS = 600


# ── Feature functions (module-level for pickling) ─────────────────────────────
def jaccard_ngram(t1: str, t2: str, k: int = 5) -> float:
    words1 = t1.lower().split()
    words2 = t2.lower().split()
    s1 = set(tuple(words1[i: i + k]) for i in range(len(words1) - k + 1))
    s2 = set(tuple(words2[i: i + k]) for i in range(len(words2) - k + 1))
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def compute_ecs(t1: str, t2: str) -> dict[str, float]:
    """ECS = IoD of inter-edit-gap lengths from word-level LCS diff."""
    w1 = t1.lower().split()
    w2 = t2.lower().split()
    total_len = max(len(w1), 1)

    matcher = difflib.SequenceMatcher(None, w1, w2, autojunk=False)
    opcodes = matcher.get_opcodes()

    edit_positions = []
    longest_run = 0
    current_run = 0

    for tag, i1, i2, j1, j2 in opcodes:
        if tag != "equal":
            mid = (i1 + i2) / 2.0
            edit_positions.append(mid)
            current_run += i2 - i1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0

    n_edits = len(edit_positions)
    edit_count_norm = n_edits / total_len

    edit_span_frac = 0.0
    if n_edits > 1:
        edit_span_frac = (edit_positions[-1] - edit_positions[0]) / total_len

    longest_run_frac = longest_run / total_len

    if n_edits < 2:
        iod = 0.0
    else:
        gaps = np.diff(edit_positions)
        mean_gap = float(np.mean(gaps))
        if mean_gap == 0:
            iod = 0.0
        else:
            iod = float(np.var(gaps) / mean_gap)
    iod = min(iod, MAX_IOD_CLIP)

    return {
        "ecs": iod,
        "edit_count": n_edits,
        "edit_count_norm": edit_count_norm,
        "edit_span_frac": edit_span_frac,
        "longest_run": longest_run_frac,
    }


def compute_features(row: tuple[str, str, int, str]) -> dict[str, Any]:
    t1, t2, label, pair_type = row
    if len(t1.split()) < 10 or len(t2.split()) < 10:
        return {"label": label, "pair_type": pair_type, "skip": True}
    jac = jaccard_ngram(t1, t2)
    ecs_feats = compute_ecs(t1, t2)
    return {"label": label, "pair_type": pair_type, "jaccard": jac, "skip": False, **ecs_feats}


# ── Dataset construction ───────────────────────────────────────────────────────
def load_articles(n: int) -> list[dict]:
    """Generate synthetic articles from topic-specific vocabularies (no network needed).

    5 categories each with ~60 distinctive words + 20 shared common words.
    Articles are 250-350 words: 80% category vocab + 20% common words.
    Hard negatives: same category (overlapping vocab → moderate Jaccard).
    Near-dups: article A with a spliced block from B (localized edit cluster).
    """
    logger.info(f"Generating {n} synthetic articles from 5 topic vocabularies...")

    categories = {
        0: ("politics", [
            "government", "senator", "president", "election", "policy", "congress",
            "democrat", "republican", "vote", "legislation", "campaign", "parliament",
            "minister", "constitution", "democracy", "bill", "committee", "federal",
            "state", "law", "party", "candidate", "ballot", "reform", "debate",
            "administration", "cabinet", "senate", "house", "speaker", "amendment",
            "judiciary", "executive", "regulation", "treaty", "diplomacy", "foreign",
            "domestic", "budget", "taxation", "healthcare", "immigration", "security",
            "military", "defense", "intelligence", "sanctions", "coalition", "majority",
            "minority", "opposition", "leadership", "summit", "agreement", "resolution",
            "veto", "impeachment", "scandal", "investigation", "testimony", "hearing",
        ]),
        1: ("sports", [
            "football", "soccer", "basketball", "baseball", "tennis", "championship",
            "athlete", "stadium", "tournament", "coach", "team", "player", "score",
            "goal", "match", "season", "league", "trophy", "medal", "training",
            "defender", "midfielder", "striker", "goalkeeper", "referee", "penalty",
            "tackle", "dribble", "sprint", "marathon", "swimming", "cycling", "rowing",
            "gymnastics", "boxing", "wrestling", "skiing", "skating", "volleyball",
            "cricket", "rugby", "polo", "golf", "victory", "defeat", "draw",
            "semifinal", "qualifier", "ranking", "transfer", "contract", "sponsor",
            "broadcast", "spectator", "fan", "arena", "pitch", "court", "track",
        ]),
        2: ("science", [
            "research", "experiment", "hypothesis", "laboratory", "molecule", "protein",
            "genome", "evolution", "quantum", "particle", "photon", "electron",
            "neuron", "antibody", "vaccine", "pathogen", "climate", "ecosystem",
            "biodiversity", "taxonomy", "astronomy", "telescope", "galaxy", "asteroid",
            "orbit", "gravity", "radiation", "isotope", "catalyst", "polymer",
            "semiconductor", "algorithm", "computation", "simulation", "dataset",
            "neural", "statistical", "empirical", "methodology", "analysis", "synthesis",
            "compound", "reaction", "entropy", "thermodynamics", "magnetism", "optics",
            "microscope", "spectroscopy", "measurement", "observation", "theory",
            "publication", "journal", "peer", "review", "citation", "discovery",
        ]),
        3: ("business", [
            "market", "revenue", "profit", "investor", "startup", "corporation",
            "merger", "acquisition", "stock", "dividend", "shareholder", "equity",
            "debt", "credit", "banking", "insurance", "commodity", "currency",
            "inflation", "recession", "growth", "gdp", "trade", "export", "import",
            "tariff", "supply", "demand", "consumer", "retail", "wholesale", "logistics",
            "manufacturing", "production", "factory", "outsourcing", "franchise",
            "brand", "marketing", "advertising", "campaign", "launch", "product",
            "service", "customer", "subscription", "pricing", "discount", "quarterly",
            "annual", "forecast", "earnings", "valuation", "funding", "venture",
            "capital", "portfolio", "hedge", "futures", "derivative", "commodity",
        ]),
        4: ("technology", [
            "software", "hardware", "processor", "memory", "network", "internet",
            "cloud", "server", "database", "encryption", "cybersecurity", "hacking",
            "blockchain", "cryptocurrency", "artificial", "intelligence", "machine",
            "learning", "algorithm", "neural", "robot", "automation", "sensor",
            "device", "smartphone", "operating", "system", "application", "platform",
            "interface", "bandwidth", "protocol", "wireless", "fiber", "latency",
            "compiler", "framework", "library", "api", "microservice", "container",
            "virtualization", "quantum", "computing", "transistor", "chip", "silicon",
            "battery", "renewable", "satellite", "streaming", "codec", "resolution",
            "pixel", "display", "camera", "printer", "storage", "backup", "recovery",
        ]),
    }
    common_words = [
        "the", "and", "that", "this", "with", "from", "have", "been", "will",
        "more", "also", "after", "some", "their", "when", "which", "said",
        "over", "such", "into", "than", "other", "could", "about", "first",
        "time", "year", "new", "last", "long", "make", "many", "well", "only",
        "two", "may", "use", "even", "most", "both", "very", "each", "where",
    ]

    rng = random.Random(SEED + 1)
    articles = []
    n_cats = len(categories)
    for i in range(n):
        cat_id = i % n_cats
        cat_name, cat_words = categories[cat_id]
        # Generate 300-word article: 78% category words, 22% common
        length = rng.randint(280, 340)
        words = []
        for _ in range(length):
            if rng.random() < 0.78:
                words.append(rng.choice(cat_words))
            else:
                words.append(rng.choice(common_words))
        text = " ".join(words)
        articles.append({"title": f"{cat_name}_{i}", "text": text, "label": cat_id})

    logger.info(f"Generated {len(articles)} synthetic articles")
    return articles


def make_near_dup(a: dict, b: dict, rng: random.Random) -> tuple[str, str]:
    """Replace a contiguous 20-40% word span of A with words from B."""
    words_a = a["text"].split()
    words_b = b["text"].split()
    n = len(words_a)
    frac = rng.uniform(0.2, 0.4)
    span = max(1, int(n * frac))
    start = rng.randint(0, max(0, n - span))
    replacement = words_b[:span]
    modified = words_a[:start] + replacement + words_a[start + span:]
    return a["text"], " ".join(modified)


def build_pairs(articles: list[dict], pairs_per_class: int, seed: int = SEED) -> list[tuple[str, str, int, str]]:
    rng = random.Random(seed)
    art_list = articles[:]
    rng.shuffle(art_list)

    # Bucket by category label for same-topic grouping
    buckets: dict[Any, list] = defaultdict(list)
    for a in art_list:
        key = a.get("label", a["title"][:4].lower())
        buckets[key].append(a)

    pairs: list[tuple[str, str, int, str]] = []

    # Near-duplicates: localized splice
    logger.info("Building near-duplicate pairs...")
    i = 0
    while len([p for p in pairs if p[2] == 1]) < pairs_per_class and i < len(art_list) - 1:
        t1, t2 = make_near_dup(art_list[i], art_list[i + 1], rng)
        pairs.append((t1, t2, 1, "near_dup"))
        i += 2

    # Hard negatives: same topic bucket, different articles
    logger.info("Building hard-negative pairs...")
    hd_pool = []
    for bucket in buckets.values():
        if len(bucket) >= 2:
            a, b = rng.sample(bucket, 2)
            hd_pool.append((a["text"], b["text"], 0, "hard_neg"))
    rng.shuffle(hd_pool)
    pairs.extend(hd_pool[:pairs_per_class])

    # Random pairs: different articles
    logger.info("Building random pairs...")
    while len([p for p in pairs if p[3] == "random"]) < pairs_per_class:
        a, b = rng.sample(art_list, 2)
        pairs.append((a["text"], b["text"], 0, "random"))

    rng.shuffle(pairs)
    logger.info(f"Built {len(pairs)} pairs total")
    return pairs


# ── Evaluation ────────────────────────────────────────────────────────────────
def evaluate_classifiers(df: pd.DataFrame) -> dict[str, Any]:
    feat_sets = {
        "jaccard_only": ["jaccard"],
        "ecs_only": ["ecs"],
        "jaccard_ecs": ["jaccard", "ecs"],
        "all_features": ["jaccard", "ecs", "edit_count_norm", "edit_span_frac", "longest_run"],
    }

    y = df["label"].values
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    results: dict[str, Any] = {}
    all_predictions: dict[str, np.ndarray] = {}

    for name, feats in feat_sets.items():
        X = df[feats].values
        aucs = []
        all_proba = np.zeros(len(df))
        for train_idx, val_idx in skf.split(X, y):
            clf = Pipeline([
                ("scaler", StandardScaler()),
                ("lr", LogisticRegression(max_iter=2000, C=1.0)),
            ])
            clf.fit(X[train_idx], y[train_idx])
            proba = clf.predict_proba(X[val_idx])[:, 1]
            aucs.append(roc_auc_score(y[val_idx], proba))
            all_proba[val_idx] = proba
        results[name] = {
            "auc_mean": float(np.mean(aucs)),
            "auc_std": float(np.std(aucs)),
            "auc_folds": [float(a) for a in aucs],
        }
        all_predictions[name] = all_proba
        logger.info(f"  {name}: AUC={np.mean(aucs):.4f} ± {np.std(aucs):.4f}")

    return results, all_predictions


def precision_at_recall(y_true: np.ndarray, scores: np.ndarray, recall_target: float = 0.8) -> float:
    from sklearn.metrics import precision_recall_curve
    prec, rec, _ = precision_recall_curve(y_true, scores)
    # Find precision at closest recall >= recall_target
    mask = rec >= recall_target
    if not mask.any():
        return float("nan")
    return float(prec[mask].max())


# ── Main ──────────────────────────────────────────────────────────────────────
@logger.catch(reraise=True)
def main(n_articles: int = N_ARTICLES, pairs_per_class: int = PAIRS_PER_CLASS) -> None:
    logger.info(f"=== ECS vs Jaccard experiment | n_articles={n_articles}, pairs_per_class={pairs_per_class} ===")

    # 1. Load articles
    articles = load_articles(n_articles)
    if len(articles) < pairs_per_class * 3:
        logger.warning(f"Only {len(articles)} articles, reducing pairs_per_class")
        pairs_per_class = max(10, len(articles) // 6)

    # 2. Build pairs
    pairs = build_pairs(articles, pairs_per_class)
    del articles
    gc.collect()

    # 3. Compute features (parallel)
    logger.info(f"Computing features for {len(pairs)} pairs with {NUM_CPUS} workers...")
    workers = max(1, NUM_CPUS - 1)
    feature_rows = []

    with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("spawn")) as pool:
        futs = {pool.submit(compute_features, row): i for i, row in enumerate(pairs)}
        for fut in as_completed(futs):
            res = fut.result()
            feature_rows.append(res)

    # Sort back by original order isn't needed; shuffle already done
    feature_rows = [r for r in feature_rows if not r.get("skip", False)]
    logger.info(f"Features computed for {len(feature_rows)} pairs (skipped {len(pairs)-len(feature_rows)})")

    df = pd.DataFrame(feature_rows)
    logger.info(f"DataFrame shape: {df.shape}")
    logger.info(f"Label distribution: {df['label'].value_counts().to_dict()}")
    logger.info(f"Pair type distribution: {df['pair_type'].value_counts().to_dict()}")

    # Quick sanity: check for NaN/inf
    n_bad = df[["jaccard", "ecs", "edit_count_norm", "edit_span_frac", "longest_run"]].isnull().sum().sum()
    n_inf = np.isinf(df[["jaccard", "ecs", "edit_count_norm", "edit_span_frac", "longest_run"]].values).sum()
    if n_bad > 0 or n_inf > 0:
        logger.warning(f"Found {n_bad} NaN and {n_inf} inf values — filling with 0")
        df = df.fillna(0)
        df = df.replace([np.inf, -np.inf], 0)

    # 4. Feature summaries
    nd = df[df["label"] == 1]
    neg = df[df["label"] == 0]
    hn = df[df["pair_type"] == "hard_neg"]
    rnd = df[df["pair_type"] == "random"]

    feature_summary = {
        "median_jaccard_near_dup": float(nd["jaccard"].median()),
        "median_jaccard_hard_neg": float(hn["jaccard"].median()) if len(hn) > 0 else None,
        "median_jaccard_random": float(rnd["jaccard"].median()) if len(rnd) > 0 else None,
        "median_ecs_near_dup": float(nd["ecs"].median()),
        "median_ecs_hard_neg": float(hn["ecs"].median()) if len(hn) > 0 else None,
        "median_ecs_random": float(rnd["ecs"].median()) if len(rnd) > 0 else None,
        "mean_ecs_near_dup": float(nd["ecs"].mean()),
        "mean_ecs_neg": float(neg["ecs"].mean()),
    }
    logger.info("Feature summary:")
    for k, v in feature_summary.items():
        logger.info(f"  {k}: {v:.4f}" if v is not None else f"  {k}: N/A")

    # 5. Mann-Whitney on ECS: near-dup vs negatives
    iod_nd = nd["ecs"].values
    iod_neg = neg["ecs"].values
    iod_hn = hn["ecs"].values if len(hn) > 0 else np.array([])

    stat_all, pval_all = mannwhitneyu(iod_nd, iod_neg, alternative="greater")
    median_ratio_all = float(np.median(iod_nd)) / (float(np.median(iod_neg)) + 1e-9)

    mw_hn = {}
    if len(iod_hn) > 0:
        stat_hn, pval_hn = mannwhitneyu(iod_nd, iod_hn, alternative="greater")
        mw_hn = {
            "statistic": float(stat_hn),
            "p_value": float(pval_hn),
            "median_iod_near_dup": float(np.median(iod_nd)),
            "median_iod_hard_neg": float(np.median(iod_hn)),
            "median_ratio": float(np.median(iod_nd)) / (float(np.median(iod_hn)) + 1e-9),
        }
        logger.info(f"MW (ND vs HN): p={pval_hn:.4f}, ratio={mw_hn['median_ratio']:.2f}")

    logger.info(f"MW (ND vs all-neg): p={pval_all:.4f}, ratio={median_ratio_all:.2f}")

    # 6. Classification
    logger.info("Running 5-fold CV classification...")
    if df["label"].nunique() < 2:
        logger.error("Only one class present — cannot evaluate")
        raise RuntimeError("Dataset has only one class")

    clf_results, all_predictions = evaluate_classifiers(df)

    # Precision@80% recall
    y_true = df["label"].values
    p80 = {}
    for name, proba in all_predictions.items():
        p80[name] = precision_at_recall(y_true, proba, 0.8)
        logger.info(f"  {name}: P@80%R={p80[name]:.4f}")

    # Hard-negative-only AUC (near_dup vs hard_neg only)
    df_hard = df[df["pair_type"].isin(["near_dup", "hard_neg"])].copy()
    hard_neg_results = {}
    if len(df_hard["label"].unique()) == 2 and len(df_hard) >= 20:
        logger.info("Computing hard-negative-only AUC...")
        y_h = df_hard["label"].values
        skf_h = StratifiedKFold(n_splits=min(5, len(df_hard) // 4), shuffle=True, random_state=SEED)
        for name, feats in [
            ("jaccard_only", ["jaccard"]),
            ("jaccard_ecs", ["jaccard", "ecs"]),
            ("all_features", ["jaccard", "ecs", "edit_count_norm", "edit_span_frac", "longest_run"]),
        ]:
            X_h = df_hard[feats].values
            aucs_h = []
            for tr, vl in skf_h.split(X_h, y_h):
                clf = Pipeline([("sc", StandardScaler()), ("lr", LogisticRegression(max_iter=2000))])
                clf.fit(X_h[tr], y_h[tr])
                proba_h = clf.predict_proba(X_h[vl])[:, 1]
                if len(np.unique(y_h[vl])) == 2:
                    aucs_h.append(roc_auc_score(y_h[vl], proba_h))
            if aucs_h:
                hard_neg_results[name] = {"auc_mean": float(np.mean(aucs_h)), "auc_std": float(np.std(aucs_h))}
                logger.info(f"  hard-neg {name}: AUC={np.mean(aucs_h):.4f}")

    # 7. Verdict
    delta_auc = clf_results["jaccard_ecs"]["auc_mean"] - clf_results["jaccard_only"]["auc_mean"]
    ecs_only_auc = clf_results["ecs_only"]["auc_mean"]
    mw_passes = pval_all < 0.05 and median_ratio_all >= 1.5
    verdict = (
        "CONFIRMED"
        if (delta_auc >= 0.03 and ecs_only_auc > 0.6 and median_ratio_all >= 2.0 and pval_all < 0.01)
        else "PARTIAL"
        if (delta_auc >= 0.01 and ecs_only_auc > 0.55 and mw_passes)
        else "DISCONFIRMED"
    )
    logger.info(f"=== VERDICT: {verdict} | delta_AUC={delta_auc:.4f}, ecs_auc={ecs_only_auc:.4f}, MW_p={pval_all:.4f} ===")

    # 8. Build method_out.json (exp_gen_sol_out schema)
    # Each pair = one example; input = "{pair_type}: [text1[:100] | text2[:100]]", output = label str
    examples = []
    for idx, row in df.reset_index(drop=True).iterrows():
        inp = f"pair_type={row['pair_type']} jaccard={row['jaccard']:.3f} ecs={row['ecs']:.2f}"
        out = str(int(row["label"]))
        examples.append({
            "input": inp,
            "output": out,
            "predict_jaccard": f"{all_predictions['jaccard_only'][idx]:.4f}",
            "predict_ecs": f"{all_predictions['ecs_only'][idx]:.4f}",
            "predict_combined": f"{all_predictions['jaccard_ecs'][idx]:.4f}",
            "predict_all_features": f"{all_predictions['all_features'][idx]:.4f}",
            "metadata_pair_type": row["pair_type"],
            "metadata_jaccard": f"{row['jaccard']:.4f}",
            "metadata_ecs": f"{row['ecs']:.4f}",
        })

    method_out = {
        "metadata": {
            "hypothesis": "ECS (IoD of inter-edit gaps) adds signal over Jaccard for near-duplicate detection",
            "method": "Edit Clustering Score (ECS) = Index of Dispersion of word-level LCS edit positions",
            "n_pairs": len(df),
            "pairs_per_class": pairs_per_class,
            "n_articles_loaded": n_articles,
            "classification_results": clf_results,
            "hard_neg_results": hard_neg_results,
            "precision_at_80pct_recall": p80,
            "mann_whitney_nd_vs_all_neg": {
                "statistic": float(stat_all),
                "p_value": float(pval_all),
                "median_iod_near_dup": float(np.median(iod_nd)),
                "median_iod_neg": float(np.median(iod_neg)),
                "median_ratio": median_ratio_all,
            },
            "mann_whitney_nd_vs_hard_neg": mw_hn,
            "feature_summary": feature_summary,
            "verdict": verdict,
            "delta_auc_combined_vs_jaccard_only": delta_auc,
        },
        "datasets": [{"dataset": "wikipedia_near_dup_synthetic", "examples": examples}],
    }

    out_path = WS / "method_out.json"
    out_path.write_text(json.dumps(method_out, indent=2))
    logger.info(f"Written {out_path} ({out_path.stat().st_size / 1e6:.1f}MB)")

    # Print summary
    logger.info("=== RESULTS SUMMARY ===")
    for name, r in clf_results.items():
        logger.info(f"  {name}: AUC={r['auc_mean']:.4f} ± {r['auc_std']:.4f}")
    logger.info(f"  delta_AUC (combined - jaccard_only): {delta_auc:+.4f}")
    logger.info(f"  MW ND vs neg: p={pval_all:.4f}, median_ratio={median_ratio_all:.2f}")
    logger.info(f"  VERDICT: {verdict}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-articles", type=int, default=N_ARTICLES)
    parser.add_argument("--pairs-per-class", type=int, default=PAIRS_PER_CLASS)
    args = parser.parse_args()
    main(n_articles=args.n_articles, pairs_per_class=args.pairs_per_class)
