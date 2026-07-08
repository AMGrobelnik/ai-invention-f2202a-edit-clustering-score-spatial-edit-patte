#!/usr/bin/env python3
"""Build 900 Wikipedia text pairs: near-duplicates, hard negatives, random pairs."""

import json
import random
import time
import resource
import sys
from pathlib import Path
from typing import Optional

import requests
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3, 8 * 1024**3))

WORKSPACE = Path(__file__).parent
random.seed(42)

UA = "AII-Research-Bot/1.0 (research@example.com)"
BASE = "https://en.wikipedia.org/w/api.php"

TOPICS = [
    "Albert Einstein", "Python programming language", "World War II", "Solar System",
    "Olympic Games", "French Revolution", "Amazon rainforest", "Jazz music",
    "Leonardo da Vinci", "DNA", "Roman Empire", "Quantum mechanics",
    "Football (soccer)", "Shakespeare", "Buddhism", "Plate tectonics",
    "Renaissance", "Internet", "Mozart", "Napoleon Bonaparte",
    "Evolution", "Ancient Egypt", "Climate change", "Jazz", "Bacteria",
    "Beethoven", "American Civil War", "Moon", "Marie Curie",
    "Photosynthesis", "Renaissance art", "Capitalism", "Democracy",
    "Stephen Hawking", "Arctic", "Coffee", "Architecture", "Chess",
    "Astronomy", "Antibiotics", "Human brain", "Impressionism",
    "Colonialism", "Artificial intelligence", "Space exploration",
    "Calculus", "Opera", "Ballet", "Medieval Europe", "Volcanoes",
    "Photography", "Samuel Taylor Coleridge", "Cricket", "Yoga",
    "Charles Darwin", "Gothic architecture", "Baroque music", "Psychology",
    "Oceanography", "Nuclear physics", "Philosophy of mind", "Surrealism",
    "Rugby", "Tennis", "Swimming", "Basketball", "Baseball",
    "Polar exploration", "Botany", "Genetics", "Ecology", "Thermodynamics",
]

# Category labels for articles (based on search topic group)
TOPIC_CATEGORIES = {
    "science": ["Albert Einstein", "DNA", "Quantum mechanics", "Evolution", "Bacteria",
                "Photosynthesis", "Climate change", "Plate tectonics", "Astronomy",
                "Human brain", "Nuclear physics", "Thermodynamics", "Genetics", "Ecology",
                "Botany", "Oceanography", "Antibiotics", "Marie Curie", "Stephen Hawking"],
    "history": ["World War II", "French Revolution", "Roman Empire", "Napoleon Bonaparte",
                "American Civil War", "Ancient Egypt", "Renaissance", "Medieval Europe",
                "Colonialism", "Polar exploration", "Charles Darwin"],
    "arts": ["Leonardo da Vinci", "Jazz music", "Shakespeare", "Mozart", "Beethoven",
             "Renaissance art", "Impressionism", "Surrealism", "Gothic architecture",
             "Baroque music", "Opera", "Ballet", "Photography"],
    "sports": ["Olympic Games", "Football (soccer)", "Cricket", "Chess", "Rugby",
               "Tennis", "Swimming", "Basketball", "Baseball", "Yoga"],
    "technology": ["Python programming language", "Internet", "Artificial intelligence",
                   "Space exploration", "Calculus"],
    "nature": ["Amazon rainforest", "Solar System", "Moon", "Arctic", "Volcanoes",
               "Coffee"],
    "society": ["Buddhism", "Capitalism", "Democracy", "Psychology", "Philosophy of mind"],
    "architecture": ["Architecture", "Samuel Taylor Coleridge"],
}

# Reverse lookup
TOPIC_TO_CAT = {}
for cat, topics in TOPIC_CATEGORIES.items():
    for t in topics:
        TOPIC_TO_CAT[t] = cat


def wiki_search(query: str, limit: int = 5) -> list[str]:
    params = {"action": "query", "list": "search", "srsearch": query,
              "format": "json", "srlimit": limit}
    for attempt in range(3):
        try:
            r = requests.get(BASE, params=params, headers={"User-Agent": UA}, timeout=15)
            if r.status_code == 429:
                time.sleep(2 + attempt * 2)
                continue
            r.raise_for_status()
            return [hit["title"] for hit in r.json()["query"]["search"]]
        except Exception as e:
            logger.debug(f"Search error {query}: {e}")
            time.sleep(1)
    return []


def wiki_extract(title: str) -> Optional[str]:
    params = {"action": "query", "prop": "extracts", "titles": title,
              "format": "json", "explaintext": True, "exsectionformat": "plain"}
    for attempt in range(3):
        try:
            r = requests.get(BASE, params=params, headers={"User-Agent": UA}, timeout=20)
            if r.status_code == 429:
                time.sleep(2 + attempt * 2)
                continue
            r.raise_for_status()
            pages = r.json()["query"]["pages"]
            page = next(iter(pages.values()))
            extract = page.get("extract", "")
            return extract if extract else None
        except Exception as e:
            logger.debug(f"Extract error {title}: {e}")
            time.sleep(1)
    return None


def jaccard_5gram(text_a: str, text_b: str) -> float:
    def ngrams(text: str):
        words = text.split()
        return set(tuple(words[i:i+5]) for i in range(len(words) - 4))
    a, b = ngrams(text_a), ngrams(text_b)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


@logger.catch(reraise=True)
def main():
    logger.info("Fetching Wikipedia articles sequentially with rate limiting...")

    all_articles: list[dict] = []
    cat_articles: dict[str, list[dict]] = {cat: [] for cat in TOPIC_CATEGORIES}

    for i, topic in enumerate(TOPICS):
        cat = TOPIC_TO_CAT.get(topic, "misc")
        # Skip if category already has enough
        if len(cat_articles.get(cat, [])) >= 40:
            continue

        titles = wiki_search(topic, limit=6)
        time.sleep(0.3)

        for title in titles[:4]:
            extract = wiki_extract(title)
            time.sleep(0.3)
            if not extract:
                continue
            words = extract.split()
            if len(words) < 80:
                continue
            text = " ".join(words[:800])
            art = {"title": title, "text": text, "word_count": len(text.split()), "category": cat}
            all_articles.append(art)
            if cat in cat_articles:
                cat_articles[cat].append(art)

        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i+1}/{len(TOPICS)} topics, total articles: {len(all_articles)}")

    logger.info(f"Total articles: {len(all_articles)}")

    # Filter cats with >=3 articles
    good_cats = {c: arts for c, arts in cat_articles.items() if len(arts) >= 3}
    logger.info(f"Usable categories: {list(good_cats.keys())}")

    if len(all_articles) < 50:
        logger.error("Too few articles")
        sys.exit(1)

    used_titles: dict[str, int] = {}
    def count_uses(title: str) -> int:
        return used_titles.get(title, 0)
    def register(a: dict, b: dict):
        used_titles[a["title"]] = count_uses(a["title"]) + 1
        used_titles[b["title"]] = count_uses(b["title"]) + 1
    MAX_USES = 20  # relaxed to allow enough pairs

    cat_list = list(good_cats.keys())

    # ---- Near duplicates ----
    logger.info("Building near-duplicate pairs...")
    nd_pairs = []
    attempts = 0
    while len(nd_pairs) < 300 and attempts < 8000:
        attempts += 1
        cat_a = random.choice(cat_list)
        art_a = random.choice(good_cats[cat_a])
        if count_uses(art_a["title"]) >= MAX_USES:
            continue
        other_cats = [c for c in cat_list if c != cat_a]
        if not other_cats:
            continue
        cat_b = random.choice(other_cats)
        art_b = random.choice(good_cats[cat_b])

        words_a = art_a["text"].split()
        words_b = art_b["text"].split()
        if len(words_a) < 100 or len(words_b) < 40:
            continue
        splice_start = int(random.uniform(0.1, 0.6) * len(words_a))
        splice_len = int(random.uniform(0.2, 0.4) * len(words_a))
        splice_len = min(splice_len, len(words_b))
        spliced = words_a[:splice_start] + words_b[:splice_len] + words_a[splice_start + splice_len:]
        text_b = " ".join(spliced)
        j = jaccard_5gram(art_a["text"], text_b)
        if j < 0.20 or j > 0.88:
            continue
        nd_pairs.append({
            "text_a": art_a["text"], "text_b": text_b,
            "jaccard_5gram": round(j, 4),
            "word_count_a": len(words_a), "word_count_b": len(spliced),
            "category": art_a["category"],
            "splice_start_pct": round(splice_start / len(words_a), 3),
            "splice_length_pct": round(splice_len / len(words_a), 3),
        })
        register(art_a, art_b)

    logger.info(f"Near-duplicate pairs: {len(nd_pairs)}")

    # ---- Hard negatives ----
    logger.info("Building hard-negative pairs...")
    hn_pairs = []
    attempts = 0
    while len(hn_pairs) < 300 and attempts < 8000:
        attempts += 1
        cat = random.choice(cat_list)
        arts = good_cats[cat]
        if len(arts) < 2:
            continue
        art_a, art_b = random.sample(arts, 2)
        if count_uses(art_a["title"]) >= MAX_USES:
            continue
        if len(art_a["text"].split()) < 100 or len(art_b["text"].split()) < 100:
            continue
        j = jaccard_5gram(art_a["text"], art_b["text"])
        if j > 0.65:
            continue
        hn_pairs.append({
            "text_a": art_a["text"], "text_b": art_b["text"],
            "jaccard_5gram": round(j, 4),
            "word_count_a": len(art_a["text"].split()),
            "word_count_b": len(art_b["text"].split()),
            "category": cat,
            "splice_start_pct": None, "splice_length_pct": None,
        })
        register(art_a, art_b)

    logger.info(f"Hard-negative pairs: {len(hn_pairs)}")

    # ---- Random pairs ----
    logger.info("Building random pairs...")
    rnd_pairs = []
    attempts = 0
    while len(rnd_pairs) < 300 and attempts < 8000:
        attempts += 1
        if len(cat_list) < 2:
            break
        cat_a, cat_b = random.sample(cat_list, 2)
        art_a = random.choice(good_cats[cat_a])
        art_b = random.choice(good_cats[cat_b])
        if count_uses(art_a["title"]) >= MAX_USES:
            continue
        if len(art_a["text"].split()) < 100 or len(art_b["text"].split()) < 100:
            continue
        j = jaccard_5gram(art_a["text"], art_b["text"])
        rnd_pairs.append({
            "text_a": art_a["text"], "text_b": art_b["text"],
            "jaccard_5gram": round(j, 4),
            "word_count_a": len(art_a["text"].split()),
            "word_count_b": len(art_b["text"].split()),
            "category": "mixed",
            "splice_start_pct": None, "splice_length_pct": None,
        })
        register(art_a, art_b)

    logger.info(f"Random pairs: {len(rnd_pairs)}")

    # ---- Assemble ----
    labeled = []
    for i, p in enumerate(nd_pairs):
        labeled.append({**p, "pair_id": f"nd_{i+1:03d}", "label": "near_duplicate", "fold": i % 5})
    for i, p in enumerate(hn_pairs):
        labeled.append({**p, "pair_id": f"hn_{i+1:03d}", "label": "hard_negative", "fold": i % 5})
    for i, p in enumerate(rnd_pairs):
        labeled.append({**p, "pair_id": f"rnd_{i+1:03d}", "label": "random", "fold": i % 5})

    random.shuffle(labeled)

    for lbl in ["near_duplicate", "hard_negative", "random"]:
        jacs = sorted([p["jaccard_5gram"] for p in labeled if p["label"] == lbl])
        if jacs:
            logger.info(f"{lbl}: n={len(jacs)} jaccard min={jacs[0]:.3f} median={jacs[len(jacs)//2]:.3f} max={jacs[-1]:.3f}")

    logger.info(f"Total pairs: {len(labeled)}")

    out = WORKSPACE / "data_out.json"
    out.write_text(json.dumps(labeled, indent=2))
    logger.info(f"Wrote {out}")

    mini = []
    for lbl in ["near_duplicate", "hard_negative", "random"]:
        mini.extend([p for p in labeled if p["label"] == lbl][:10])
    (WORKSPACE / "data_out_mini.json").write_text(json.dumps(mini, indent=2))

    preview = []
    for lbl in ["near_duplicate", "hard_negative", "random"]:
        for item in [p for p in labeled if p["label"] == lbl][:3]:
            preview.append({**item, "text_a": item["text_a"][:200], "text_b": item["text_b"][:200]})
    (WORKSPACE / "data_out_preview.json").write_text(json.dumps(preview, indent=2))

    logger.info("Done.")


if __name__ == "__main__":
    main()
