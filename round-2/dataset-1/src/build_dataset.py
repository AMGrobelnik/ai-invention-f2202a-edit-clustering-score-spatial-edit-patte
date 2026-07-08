#!/usr/bin/env python3
"""Build Wikipedia boilerplate hard-negative benchmark dataset."""

import json
import re
import time
import random
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import sys
import resource

from loguru import logger

WORKSPACE = Path(__file__).parent
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(str(WORKSPACE / "logs/run.log"), level="DEBUG", rotation="30 MB")

# Memory limit: 20GB
resource.setrlimit(resource.RLIMIT_AS, (20 * 1024**3, 20 * 1024**3))

CACHE_DIR = WORKSPACE / "temp/article_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "WikipediaBenchmarkBuilder/1.0 (research; mailto:research@example.com)"}

# Extended boilerplate (~400 words)
BOILERPLATE = (
    "This article uses material from the Wikipedia article, which is released under the "
    "Creative Commons Attribution-Share-Alike License 3.0. Wikipedia is a free encyclopedia "
    "that anyone can edit. The text of this article is available under the Creative Commons "
    "Attribution-ShareAlike License. Additional terms may apply. By using this site, you agree "
    "to the Terms of Use and Privacy Policy. Wikipedia is a registered trademark of the "
    "Wikimedia Foundation, Inc., a non-profit organization. This content may be copied, "
    "modified, and redistributed under the terms of the Creative Commons Attribution-ShareAlike "
    "License version 3.0. For more information, please visit the Wikimedia Foundation website. "
    "All text is available under the terms of the GNU Free Documentation License. The Wikipedia "
    "content has been used in accordance with the CC BY-SA 3.0 license requirements. "
    "Content contributed to Wikipedia is released under this free license. "
    "Permission is granted to copy, distribute and modify this document under the terms of "
    "the GNU Free Documentation License, Version 1.2 or any later version published by the "
    "Free Software Foundation. A copy of the license is included in the section entitled "
    "GNU Free Documentation License. Subject to disclaimers. Wikipedia makes no guarantee "
    "of validity. Wikipedia is not responsible for errors or omissions in its content. "
    "The Wikimedia Foundation is a non-profit charitable organization. Donations support "
    "the continued development of Wikipedia and its sister projects including Wiktionary, "
    "Wikisource, Wikibooks, and Wikimedia Commons. The content of Wikipedia is freely "
    "available under open licenses and may be reused with attribution in compliance with "
    "the terms of the Creative Commons Attribution-ShareAlike License version 3.0 or later. "
    "Users who contribute to Wikipedia agree to license their contributions under this license. "
    "Wikipedia content is not a substitute for professional advice in legal, medical, financial, "
    "or other matters. Always seek the advice of qualified professionals regarding any questions. "
    "This page was last edited by multiple contributors. For a complete list of authors, "
    "see the page history. Text is available under the Creative Commons Attribution-ShareAlike "
    "License 4.0. Images and media may be under different licenses. See each file for details. "
    "Wikipedia is hosted by the Wikimedia Foundation, a non-profit organization that also "
    "hosts a range of other projects. This site uses cookies. By continuing to browse the site "
    "you are agreeing to our use of cookies in accordance with the Cookie Policy. "
    "Wikimedia Foundation Privacy Policy applies to all Wikimedia projects and properties. "
    "The Wikimedia Foundation operates some of the world's largest collaboratively edited "
    "reference projects, including Wikipedia, the free encyclopedia. Wikipedia is available "
    "in over three hundred languages and continues to grow. The mission of the Wikimedia "
    "Foundation is to empower and engage people around the world to collect and develop "
    "educational content under a free license or in the public domain. All structured data "
    "from the main, property and lexeme namespaces is available under the Creative Commons "
    "CC0 License. Unstructured text is available under the Creative Commons Attribution-ShareAlike "
    "License. Additional terms may apply to media files from Wikimedia Commons. "
)

BP_WORDS = BOILERPLATE.split()


def clean_text(text: str) -> str:
    text = re.sub(r"==+[^=]+=+", " ", text)
    text = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", text)
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    text = re.sub(r"\[https?://\S+[^\]]*\]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(text.split())


def ngram_jaccard(text_a: str, text_b: str, n: int) -> float:
    tokens_a = text_a.lower().split()
    tokens_b = text_b.lower().split()
    if len(tokens_a) < n or len(tokens_b) < n:
        return 0.0
    grams_a = frozenset(tuple(tokens_a[i:i+n]) for i in range(len(tokens_a) - n + 1))
    grams_b = frozenset(tuple(tokens_b[i:i+n]) for i in range(len(tokens_b) - n + 1))
    inter = len(grams_a & grams_b)
    union = len(grams_a | grams_b)
    return inter / union if union > 0 else 0.0


def fetch_random_articles_batch(n: int = 50) -> list[str]:
    """Fetch n random Wikipedia article titles."""
    import requests
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query", "list": "random", "rnnamespace": 0,
        "rnlimit": min(n, 500), "format": "json",
    }
    try:
        r = requests.get(url, params=params, timeout=20, headers=HEADERS)
        data = r.json()
        return [item["title"] for item in data.get("query", {}).get("random", [])]
    except Exception as e:
        logger.warning(f"Random fetch failed: {e}")
        return []


def fetch_article_text(title: str) -> Optional[str]:
    cache_key = hashlib.md5(title.encode()).hexdigest()
    cache_path = CACHE_DIR / (cache_key + ".txt")
    if cache_path.exists():
        txt = cache_path.read_text(encoding="utf-8")
        return txt if txt else None

    import requests
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query", "prop": "extracts", "explaintext": "1",
        "titles": title, "format": "json", "exsectionformat": "plain",
        "exchars": 10000,
    }
    try:
        r = requests.get(url, params=params, timeout=20, headers=HEADERS)
        pages = r.json().get("query", {}).get("pages", {})
        text = next(iter(pages.values())).get("extract", "")
        text = clean_text(text)
        cache_path.write_text(text, encoding="utf-8")
        return text if text else None
    except Exception as e:
        logger.warning(f"Article {title!r} failed: {e}")
        cache_path.write_text("", encoding="utf-8")
        return None


def load_from_cache(min_words: int = 80) -> list[str]:
    """Load all valid article texts from the local cache."""
    texts = []
    for f in CACHE_DIR.glob("*.txt"):
        txt = f.read_text(encoding="utf-8")
        if txt and word_count(txt) >= min_words:
            texts.append(txt)
    logger.info(f"Loaded {len(texts)} articles from cache")
    return texts


def collect_articles(target: int = 1500) -> list[str]:
    """Collect target valid Wikipedia article texts, using cache first."""
    # Load cached articles
    cached = load_from_cache(min_words=80)
    if len(cached) >= target:
        logger.info(f"Cache has {len(cached)} articles (>= target {target})")
        return cached[:target]

    logger.info(f"Cache has {len(cached)}, need {target - len(cached)} more via API")
    all_articles = list(cached)
    batch_num = 0
    consecutive_failures = 0

    while len(all_articles) < target and consecutive_failures < 10:
        batch_num += 1
        titles = fetch_random_articles_batch(50)
        if not titles:
            consecutive_failures += 1
            time.sleep(3)
            continue
        consecutive_failures = 0

        def fetch_one(title: str) -> Optional[str]:
            txt = fetch_article_text(title)
            time.sleep(0.1)
            return txt

        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = [ex.submit(fetch_one, t) for t in titles]
            for fut in as_completed(futures):
                txt = fut.result()
                if txt and 80 <= word_count(txt) <= 5000:
                    all_articles.append(txt)

        logger.info(f"Batch {batch_num}: {len(all_articles)}/{target} articles")
        time.sleep(1)

    logger.info(f"Collected {len(all_articles)} total articles")
    return all_articles


def build_near_duplicate_pairs(articles: list[str], n_pairs: int = 300) -> list[dict]:
    pairs = []
    idxs = list(range(len(articles)))
    attempts = 0
    while len(pairs) < n_pairs and attempts < n_pairs * 20:
        attempts += 1
        i, j = random.sample(idxs, 2)
        text_a = articles[i]
        donor = articles[j]
        words_a = text_a.split()
        words_donor = donor.split()
        n = len(words_a)
        if n < 150:
            continue
        frac = random.uniform(0.20, 0.30)
        span = max(1, int(n * frac))
        start = random.randint(0, n - span - 1)
        donor_span = words_donor[:span]
        if not donor_span:
            continue
        spliced = words_a[:start] + donor_span + words_a[start + span:]
        text_b = " ".join(spliced)
        if word_count(text_b) < 100:
            continue
        j5 = ngram_jaccard(text_a, text_b, 5)
        j2 = ngram_jaccard(text_a, text_b, 2)
        pairs.append({
            "pair_id": len(pairs),
            "text_a": text_a,
            "text_b": text_b,
            "label": "near_duplicate",
            "fold": len(pairs) % 5,
            "jaccard_5gram": round(j5, 4),
            "jaccard_2gram": round(j2, 4),
            "boilerplate_frac": 0.0,
        })
    logger.info(f"Built {len(pairs)} near-duplicate pairs in {attempts} attempts")
    return pairs


def build_boilerplate_pairs(articles: list[str], n_pairs: int = 300) -> list[dict]:
    pairs = []
    idxs = list(range(len(articles)))
    attempts = 0
    max_bp = len(BP_WORDS)

    # Try bp lengths from large to small to find the window
    bp_lengths = [400, 300, 500, 200, max_bp, 150, 100, 600, 700]

    while len(pairs) < n_pairs and attempts < n_pairs * 60:
        attempts += 1
        i, j = random.sample(idxs, 2)
        art_c = articles[i]
        art_d = articles[j]
        wc_c = word_count(art_c)
        wc_d = word_count(art_d)
        if wc_c < 80 or wc_d < 80:
            continue

        found = False
        for bp_len in bp_lengths:
            # Repeat boilerplate if needed
            actual_words = (BP_WORDS * ((bp_len // max_bp) + 2))[:bp_len]
            bp_text = " ".join(actual_words)
            text_a = bp_text + " " + art_c
            text_b = bp_text + " " + art_d
            j5 = ngram_jaccard(text_a, text_b, 5)
            if 0.25 <= j5 <= 0.65:
                j2 = ngram_jaccard(text_a, text_b, 2)
                bp_frac = bp_len / word_count(text_a)
                pairs.append({
                    "pair_id": 300 + len(pairs),
                    "text_a": text_a,
                    "text_b": text_b,
                    "label": "boilerplate_hard_negative",
                    "fold": len(pairs) % 5,
                    "jaccard_5gram": round(j5, 4),
                    "jaccard_2gram": round(j2, 4),
                    "boilerplate_frac": round(bp_frac, 4),
                })
                found = True
                break

        if len(pairs) % 50 == 0 and found:
            logger.info(f"Boilerplate pairs: {len(pairs)}/{n_pairs} (attempts={attempts})")

    logger.info(f"Built {len(pairs)} boilerplate pairs in {attempts} attempts")
    return pairs


def build_random_pairs(articles: list[str], n_pairs: int = 300) -> list[dict]:
    pairs = []
    idxs = list(range(len(articles)))
    attempts = 0
    while len(pairs) < n_pairs and attempts < n_pairs * 20:
        attempts += 1
        i, j = random.sample(idxs, 2)
        text_a = articles[i]
        text_b = articles[j]
        if word_count(text_a) < 100 or word_count(text_b) < 100:
            continue
        j5 = ngram_jaccard(text_a, text_b, 5)
        if j5 >= 0.15:
            continue
        j2 = ngram_jaccard(text_a, text_b, 2)
        pairs.append({
            "pair_id": 600 + len(pairs),
            "text_a": text_a,
            "text_b": text_b,
            "label": "random",
            "fold": len(pairs) % 5,
            "jaccard_5gram": round(j5, 4),
            "jaccard_2gram": round(j2, 4),
            "boilerplate_frac": 0.0,
        })
    logger.info(f"Built {len(pairs)} random pairs in {attempts} attempts")
    return pairs


def validate(data: list[dict]) -> None:
    labels = [d["label"] for d in data]
    nd = labels.count("near_duplicate")
    bp = labels.count("boilerplate_hard_negative")
    rnd = labels.count("random")
    logger.info(f"Label counts: near_duplicate={nd}, boilerplate_hard_negative={bp}, random={rnd}")
    assert nd >= 50, f"Too few near_dup={nd}"
    assert bp >= 50, f"Too few bp_hn={bp}"
    assert rnd >= 50, f"Too few random={rnd}"
    for d in data:
        if d["label"] == "boilerplate_hard_negative":
            assert 0.20 <= d["jaccard_5gram"] <= 0.70, f"j5={d['jaccard_5gram']} id={d['pair_id']}"
    folds = set(d["fold"] for d in data)
    assert len(folds) >= 3, f"Too few folds: {folds}"
    logger.info("Validation passed!")


@logger.catch(reraise=True)
def main():
    random.seed(42)
    logger.info("Starting Wikipedia benchmark dataset construction")

    articles = collect_articles(target=500)
    logger.info(f"Total articles: {len(articles)}")

    # Quick Jaccard test to calibrate boilerplate length
    sample_a, sample_b = articles[0], articles[1]
    for bp_len in [100, 200, 300, 400, 500]:
        actual_words = (BP_WORDS * ((bp_len // len(BP_WORDS)) + 2))[:bp_len]
        bp_text = " ".join(actual_words)
        j = ngram_jaccard(bp_text + " " + sample_a, bp_text + " " + sample_b, 5)
        logger.info(f"  bp_len={bp_len} → j5={j:.3f} (articles: {word_count(sample_a)}/{word_count(sample_b)} words)")

    logger.info("Building near-duplicate pairs...")
    nd_pairs = build_near_duplicate_pairs(articles, 300)

    logger.info("Building boilerplate hard-negative pairs...")
    bp_pairs = build_boilerplate_pairs(articles, 300)

    logger.info("Building random pairs...")
    rnd_pairs = build_random_pairs(articles, 300)

    all_pairs = nd_pairs + bp_pairs + rnd_pairs
    random.shuffle(all_pairs)
    for i, p in enumerate(all_pairs):
        p["pair_id"] = i

    validate(all_pairs)

    out_path = WORKSPACE / "data_out.json"
    out_path.write_text(json.dumps(all_pairs, indent=2), encoding="utf-8")
    size_mb = out_path.stat().st_size / 1e6
    logger.info(f"Wrote {len(all_pairs)} pairs to {out_path} ({size_mb:.1f} MB)")

    bp_j5 = [p["jaccard_5gram"] for p in all_pairs if p["label"] == "boilerplate_hard_negative"]
    nd_j5 = [p["jaccard_5gram"] for p in all_pairs if p["label"] == "near_duplicate"]
    rnd_j5 = [p["jaccard_5gram"] for p in all_pairs if p["label"] == "random"]
    if nd_j5:
        logger.info(f"near_duplicate j5: mean={sum(nd_j5)/len(nd_j5):.3f} min={min(nd_j5):.3f} max={max(nd_j5):.3f}")
    if bp_j5:
        logger.info(f"boilerplate_hn j5: mean={sum(bp_j5)/len(bp_j5):.3f} min={min(bp_j5):.3f} max={max(bp_j5):.3f}")
    if rnd_j5:
        logger.info(f"random j5: mean={sum(rnd_j5)/len(rnd_j5):.3f} min={min(rnd_j5):.3f} max={max(rnd_j5):.3f}")


if __name__ == "__main__":
    main()
