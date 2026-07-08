#!/usr/bin/env python3
"""ECS vs Jaccard evaluation: generate dataset, compute features, run all stats."""

import sys
import json
import random
import difflib
import math
import gc
import resource
from pathlib import Path
from collections import defaultdict

import numpy as np
from loguru import logger
from scipy.stats import mannwhitneyu
from sklearn.metrics import roc_auc_score

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

WORKSPACE = Path(__file__).parent
RANDOM_SEED = 42
PAIRS_PER_CLASS = 300
N_ARTICLES = 3000
BOOTSTRAP_B = 2000

# Memory limit: 8 GB (well within 29 GB container)
RAM_BUDGET = 8 * 1024 ** 3
_avail = resource.getrlimit(resource.RLIMIT_AS)[0]
try:
    resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET * 3, RAM_BUDGET * 3))
except Exception:
    pass

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ─── Feature functions ───────────────────────────────────────────────────────

def jaccard_5gram(t1: str, t2: str) -> float:
    def shingles(text: str, k: int = 5):
        words = text.lower().split()
        return set(tuple(words[i:i+k]) for i in range(len(words)-k+1))
    s1, s2 = shingles(t1), shingles(t2)
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def compute_ecs(t1: str, t2: str) -> dict:
    """Compute ECS (IoD of inter-edit-gap lengths) and auxiliary features."""
    w1 = t1.lower().split()
    w2 = t2.lower().split()
    total_len = len(w1)
    matcher = difflib.SequenceMatcher(None, w1, w2, autojunk=False)
    opcodes = matcher.get_opcodes()

    edit_positions = []
    run = 0
    max_run = 0
    for tag, i1, i2, j1, j2 in opcodes:
        if tag != 'equal':
            mid = (i1 + i2) / 2.0
            edit_positions.append(mid)
            run += (i2 - i1)
            max_run = max(max_run, run)
        else:
            run = 0

    n_edits = len(edit_positions)
    edit_count_norm = n_edits / max(total_len, 1)
    longest_run = max_run / max(total_len, 1)
    edit_span_frac = 0.0

    if n_edits >= 2:
        edit_span_frac = (edit_positions[-1] - edit_positions[0]) / max(total_len, 1)
        gaps = np.diff(edit_positions)
        mean_gap = float(np.mean(gaps))
        iod = float(np.var(gaps) / mean_gap) if mean_gap > 0 else 0.0
    else:
        iod = 0.0

    return {
        'ecs': iod,
        'edit_count': n_edits,
        'edit_count_norm': edit_count_norm,
        'edit_span_frac': edit_span_frac,
        'longest_run': longest_run,
    }


# ─── Dataset construction ────────────────────────────────────────────────────

def load_articles(n: int) -> list[dict]:
    logger.info(f"Loading up to {n} Wikipedia articles (streaming)...")
    from datasets import load_dataset
    wiki = load_dataset('wikimedia/wikipedia', '20231101.en', split='train', streaming=True)
    articles = []
    for art in wiki:
        words = art['text'].split()[:700]
        text = ' '.join(words)
        if len(words) >= 100:
            articles.append({'title': art['title'], 'text': text})
        if len(articles) >= n:
            break
    logger.info(f"Loaded {len(articles)} articles")
    return articles


def make_near_dup(a: dict, b: dict, rng: random.Random) -> tuple[str, str]:
    words_a = a['text'].split()
    words_b = b['text'].split()
    n = len(words_a)
    frac = rng.uniform(0.2, 0.4)
    span = max(1, int(n * frac))
    start = rng.randint(0, max(0, n - span))
    replacement = words_b[:span]
    modified = words_a[:start] + replacement + words_a[start+span:]
    return a['text'], ' '.join(modified)


def build_dataset(articles: list[dict], pairs_per_class: int, rng: random.Random) -> list[dict]:
    buckets = defaultdict(list)
    for a in articles:
        key = a['title'][:4].lower()
        buckets[key].append(a)

    art_list = list(articles)
    rng.shuffle(art_list)

    pairs = []

    # Near-duplicates
    used = set()
    i = 0
    while len(pairs) < pairs_per_class and i + 1 < len(art_list):
        if i not in used and i+1 not in used:
            t1, t2 = make_near_dup(art_list[i], art_list[i+1], rng)
            wc = (len(t1.split()) + len(t2.split())) // 2
            pairs.append({'text1': t1, 'text2': t2, 'label': 1, 'pair_type': 'near_dup', 'avg_words': wc})
            used.add(i); used.add(i+1)
        i += 2

    logger.info(f"Near-duplicates: {sum(1 for p in pairs if p['label']==1)}")

    # Hard negatives (same-bucket, different articles)
    hd = []
    bucket_list = [b for b in buckets.values() if len(b) >= 2]
    rng.shuffle(bucket_list)
    for bucket in bucket_list:
        sample = rng.sample(bucket, 2)
        t1, t2 = sample[0]['text'], sample[1]['text']
        wc = (len(t1.split()) + len(t2.split())) // 2
        hd.append({'text1': t1, 'text2': t2, 'label': 0, 'pair_type': 'hard_neg', 'avg_words': wc})
    rng.shuffle(hd)
    pairs.extend(hd[:pairs_per_class])
    logger.info(f"Hard negatives: {sum(1 for p in pairs if p['pair_type']=='hard_neg')}")

    # Random pairs
    remaining = [a for j, a in enumerate(art_list) if j not in used]
    for _ in range(pairs_per_class):
        if len(remaining) < 2:
            break
        s = rng.sample(remaining, 2)
        t1, t2 = s[0]['text'], s[1]['text']
        wc = (len(t1.split()) + len(t2.split())) // 2
        pairs.append({'text1': t1, 'text2': t2, 'label': 0, 'pair_type': 'random', 'avg_words': wc})

    rng.shuffle(pairs)
    logger.info(f"Total pairs: {len(pairs)} ({sum(1 for p in pairs if p['label']==1)} pos)")
    return pairs


def compute_features(pairs: list[dict]) -> list[dict]:
    logger.info("Computing features for all pairs...")
    results = []
    for i, p in enumerate(pairs):
        if i % 100 == 0:
            logger.info(f"  {i}/{len(pairs)}")
        jac = jaccard_5gram(p['text1'], p['text2'])
        ecs_feats = compute_ecs(p['text1'], p['text2'])
        results.append({
            **p,
            'jaccard': jac,
            **ecs_feats,
        })
    logger.info("Features computed.")
    return results


# ─── Evaluation metrics ──────────────────────────────────────────────────────

def bootstrap_auc_delta(y_true, score1, score2, B: int = 2000, seed: int = 0) -> tuple[float, float]:
    """Bootstrap CI for AUC(score2) - AUC(score1)."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    deltas = []
    for _ in range(B):
        idx = rng.integers(0, n, size=n)
        yt = y_true[idx]
        if len(np.unique(yt)) < 2:
            continue
        d = roc_auc_score(yt, score2[idx]) - roc_auc_score(yt, score1[idx])
        deltas.append(d)
    deltas = np.array(deltas)
    return float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))


def confusion_at_recall(y_true, scores, target_recall: float = 0.8) -> dict:
    """Find threshold achieving >= target_recall; report confusion matrix."""
    thresholds = np.sort(np.unique(scores))[::-1]
    best = None
    for thr in thresholds:
        pred = (scores >= thr).astype(int)
        tp = int(np.sum((pred == 1) & (y_true == 1)))
        fn = int(np.sum((pred == 0) & (y_true == 1)))
        fp = int(np.sum((pred == 1) & (y_true == 0)))
        tn = int(np.sum((pred == 0) & (y_true == 0)))
        recall = tp / max(tp + fn, 1)
        if recall >= target_recall:
            prec = tp / max(tp + fp, 1)
            best = {'threshold': float(thr), 'precision': prec, 'recall': recall,
                    'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn}
            break
    if best is None:
        best = {'threshold': float(thresholds[-1]), 'precision': 0.0, 'recall': 0.0,
                'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}
    return best


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    pooled_std = math.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    return float((np.mean(a) - np.mean(b)) / pooled_std) if pooled_std > 0 else 0.0


def length_bucket(avg_words: float) -> str:
    if avg_words < 200:
        return '<200'
    elif avg_words <= 500:
        return '200-500'
    else:
        return '>500'


@logger.catch(reraise=True)
def main():
    rng = random.Random(RANDOM_SEED)

    articles = load_articles(N_ARTICLES)
    pairs = build_dataset(articles, PAIRS_PER_CLASS, rng)
    del articles; gc.collect()

    data = compute_features(pairs)
    del pairs; gc.collect()

    # ── Hard-negative subset (near-dup vs hard-neg only) ──
    hard_subset = [d for d in data if d['pair_type'] in ('near_dup', 'hard_neg')]
    logger.info(f"Hard-neg subset: {len(hard_subset)} pairs")

    y_hard = np.array([d['label'] for d in hard_subset])
    jac_hard = np.array([d['jaccard'] for d in hard_subset])
    ecs_hard = np.array([d['ecs'] for d in hard_subset])
    combined_hard = jac_hard + 0.3 * ecs_hard  # simple linear combination

    auc_jac = float(roc_auc_score(y_hard, jac_hard))
    auc_combined = float(roc_auc_score(y_hard, combined_hard))
    auc_ecs_only = float(roc_auc_score(y_hard, ecs_hard))
    delta_auc = auc_combined - auc_jac
    logger.info(f"AUC Jaccard={auc_jac:.4f}  Combined={auc_combined:.4f}  ECS-only={auc_ecs_only:.4f}  delta={delta_auc:.4f}")

    ci_low, ci_high = bootstrap_auc_delta(y_hard, jac_hard, combined_hard, B=BOOTSTRAP_B)
    logger.info(f"Bootstrap 95% CI for delta_AUC: [{ci_low:.4f}, {ci_high:.4f}]")

    # ── IoD ratio ──
    iod_ndup = np.array([d['ecs'] for d in hard_subset if d['pair_type'] == 'near_dup'])
    iod_hneg = np.array([d['ecs'] for d in hard_subset if d['pair_type'] == 'hard_neg'])
    med_ndup = float(np.median(iod_ndup))
    med_hneg = float(np.median(iod_hneg))
    iod_ratio = med_ndup / med_hneg if med_hneg > 0 else float('inf')
    mw = mannwhitneyu(iod_ndup, iod_hneg, alternative='greater')
    mw_p = float(mw.pvalue)
    logger.info(f"Median IoD: ndup={med_ndup:.4f} hneg={med_hneg:.4f} ratio={iod_ratio:.3f} p={mw_p:.4e}")

    # ── Cohen's d on log-IoD ──
    eps = 1e-6
    log_ndup = np.log(iod_ndup + eps)
    log_hneg = np.log(iod_hneg + eps)
    cd = cohens_d(log_ndup, log_hneg)
    logger.info(f"Cohen's d on log-IoD: {cd:.4f}")

    # ── Length-stratified AUC ──
    buckets_map = defaultdict(list)
    for d in hard_subset:
        b = length_bucket(d['avg_words'])
        buckets_map[b].append(d)

    length_strata_aucs = []
    for bkt in ['<200', '200-500', '>500']:
        items = buckets_map[bkt]
        if len(items) < 10:
            length_strata_aucs.append({'bucket': bkt, 'n': len(items), 'auc_jaccard': None, 'auc_combined': None})
            continue
        yb = np.array([d['label'] for d in items])
        if len(np.unique(yb)) < 2:
            length_strata_aucs.append({'bucket': bkt, 'n': len(items), 'auc_jaccard': None, 'auc_combined': None})
            continue
        jb = np.array([d['jaccard'] for d in items])
        eb = np.array([d['ecs'] for d in items])
        cb = jb + 0.3 * eb
        a_j = float(roc_auc_score(yb, jb))
        a_c = float(roc_auc_score(yb, cb))
        logger.info(f"  Bucket {bkt}: n={len(items)} AUC_jac={a_j:.4f} AUC_comb={a_c:.4f}")
        length_strata_aucs.append({'bucket': bkt, 'n': len(items), 'auc_jaccard': a_j, 'auc_combined': a_c})

    # ── Confusion matrix at 80% recall ──
    conf_jac = confusion_at_recall(y_hard, jac_hard)
    conf_comb = confusion_at_recall(y_hard, combined_hard)
    prec_gain = conf_comb['precision'] - conf_jac['precision']
    logger.info(f"Confusion @80% recall: Jac prec={conf_jac['precision']:.4f}  Comb prec={conf_comb['precision']:.4f}  gain={prec_gain:.4f}")

    # ── Verdicts ──
    verdict_auc = 'CONFIRMED' if delta_auc >= 0.03 and ci_low > 0 else \
                  ('PARTIAL' if delta_auc >= 0.03 else 'DISCONFIRMED')
    verdict_ecs_alone = 'CONFIRMED' if auc_ecs_only > 0.65 else 'DISCONFIRMED'
    verdict_iod = 'CONFIRMED' if iod_ratio >= 2.0 and mw_p < 0.01 else \
                  ('PARTIAL' if iod_ratio >= 1.5 else 'DISCONFIRMED')
    confirmed = sum([v == 'CONFIRMED' for v in [verdict_auc, verdict_ecs_alone, verdict_iod]])
    partial = sum([v == 'PARTIAL' for v in [verdict_auc, verdict_ecs_alone, verdict_iod]])
    if confirmed >= 2:
        verdict_overall = 'CONFIRMED'
    elif confirmed + partial >= 2:
        verdict_overall = 'PARTIAL'
    else:
        verdict_overall = 'DISCONFIRMED'

    narrative = (
        f"ECS (Index of Dispersion of inter-edit gaps) was evaluated against Jaccard 5-gram similarity "
        f"on {len(hard_subset)} near-duplicate vs hard-negative Wikipedia pairs. "
        f"(1) AUC improvement: Jaccard={auc_jac:.3f}, Jaccard+ECS={auc_combined:.3f}, "
        f"delta={delta_auc:.3f} (95% CI [{ci_low:.3f},{ci_high:.3f}]) → {verdict_auc}. "
        f"(2) ECS-alone AUC={auc_ecs_only:.3f} → {verdict_ecs_alone}. "
        f"(3) Median IoD ratio={iod_ratio:.2f} (ndup={med_ndup:.3f}, hneg={med_hneg:.3f}), "
        f"Mann-Whitney p={mw_p:.3e}, Cohen's d={cd:.2f} → {verdict_iod}. "
        f"Precision at 80% recall: Jaccard={conf_jac['precision']:.3f}, Combined={conf_comb['precision']:.3f} "
        f"(gain={prec_gain:+.3f}). Overall: {verdict_overall}."
    )
    logger.info(f"Narrative: {narrative}")

    # ── Build eval_out.json (exp_eval_sol_out schema) ──
    examples = []
    for d in data:
        b = length_bucket(d['avg_words'])
        jac = d['jaccard']
        ecs = d['ecs']
        comb = jac + 0.3 * ecs
        examples.append({
            'input': f"pair_type={d['pair_type']} avg_words={d['avg_words']}",
            'output': str(d['label']),
            'predict_jaccard': str(round(jac, 6)),
            'predict_combined': str(round(comb, 6)),
            'predict_ecs': str(round(ecs, 6)),
            'eval_label': float(d['label']),
            'eval_jaccard': jac,
            'eval_ecs': ecs,
            'eval_combined': comb,
            'metadata_pair_type': d['pair_type'],
            'metadata_avg_words': d['avg_words'],
            'metadata_length_bucket': b,
        })

    eval_out = {
        'metadata': {
            'evaluation_name': 'ECS vs Jaccard Stats Validation',
            'n_pairs': len(data),
            'n_hard_subset': len(hard_subset),
            'bootstrap_B': BOOTSTRAP_B,
            'pairs_per_class': PAIRS_PER_CLASS,
        },
        'metrics_agg': {
            'auc_jaccard': round(auc_jac, 6),
            'auc_ecs_jaccard': round(auc_combined, 6),
            'auc_ecs_only': round(auc_ecs_only, 6),
            'delta_auc': round(delta_auc, 6),
            'delta_auc_ci_low': round(ci_low, 6),
            'delta_auc_ci_high': round(ci_high, 6),
            'median_iod_ndup': round(med_ndup, 6),
            'median_iod_hardneg': round(med_hneg, 6),
            'iod_ratio': round(iod_ratio, 6),
            'mannwhitney_p': round(mw_p, 8),
            'cohens_d_log_iod': round(cd, 6),
            'precision_gain_at_80_recall': round(prec_gain, 6),
            'n_confirmed': float(confirmed),
            'n_partial': float(partial),
        },
        'datasets': [{
            'dataset': 'wikipedia_near_dup_eval',
            'examples': examples,
        }],
    }

    # Attach extra info as metadata (not in schema required fields)
    eval_out['metadata']['length_strata_aucs'] = length_strata_aucs
    eval_out['metadata']['confusion_jaccard'] = conf_jac
    eval_out['metadata']['confusion_combined'] = conf_comb
    eval_out['metadata']['verdict_auc_improvement'] = verdict_auc
    eval_out['metadata']['verdict_ecs_alone'] = verdict_ecs_alone
    eval_out['metadata']['verdict_iod_ratio'] = verdict_iod
    eval_out['metadata']['verdict_overall'] = verdict_overall
    eval_out['metadata']['narrative'] = narrative

    out_path = WORKSPACE / 'eval_out.json'
    out_path.write_text(json.dumps(eval_out, indent=2))
    logger.info(f"Saved eval_out.json ({out_path.stat().st_size/1024:.1f} KB)")


if __name__ == '__main__':
    main()
