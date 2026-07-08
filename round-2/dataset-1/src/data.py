#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["loguru"]
# ///
"""Load Wikipedia boilerplate benchmark and produce full_data_out.json."""

import json
import sys
from pathlib import Path
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")

WORKSPACE = Path(__file__).parent


def main() -> None:
    data_path = WORKSPACE / "data_out.json"
    logger.info(f"Loading dataset from {data_path}")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    logger.info(f"Loaded {len(data)} pairs")

    examples = []
    for pair in data:
        text_a = pair["text_a"]
        text_b = pair["text_b"]
        inp = json.dumps({"text_a": text_a, "text_b": text_b}, ensure_ascii=False)
        ex = {
            "input": inp,
            "output": pair["label"],
            "metadata_pair_id": pair["pair_id"],
            "metadata_label": pair["label"],
            "metadata_fold": pair["fold"],
            "metadata_jaccard_5gram": pair["jaccard_5gram"],
            "metadata_jaccard_2gram": pair["jaccard_2gram"],
            "metadata_boilerplate_frac": pair["boilerplate_frac"],
            "metadata_task_type": "classification",
            "metadata_n_classes": 3,
        }
        examples.append(ex)

    out = {
        "metadata": {
            "source": "wikipedia_api",
            "description": (
                "Boilerplate Hard-Negative Wikipedia Benchmark: 900 text pairs across 3 classes. "
                "NEAR-DUPLICATE: splice of 20-30% word block from a donor article. "
                "BOILERPLATE-HARD-NEGATIVE: two unrelated articles prepended with identical ~150-400-word "
                "CC-BY-SA license block, validated 5-gram Jaccard in [0.25, 0.65]. "
                "RANDOM: unrelated article pairs with Jaccard < 0.15."
            ),
            "n_pairs": len(data),
            "label_counts": {
                "near_duplicate": sum(1 for d in data if d["label"] == "near_duplicate"),
                "boilerplate_hard_negative": sum(1 for d in data if d["label"] == "boilerplate_hard_negative"),
                "random": sum(1 for d in data if d["label"] == "random"),
            },
        },
        "datasets": [
            {
                "dataset": "wikipedia_boilerplate_benchmark",
                "examples": examples,
            }
        ],
    }

    out_path = WORKSPACE / "full_data_out.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    size_mb = out_path.stat().st_size / 1e6
    logger.info(f"Wrote {len(examples)} examples to {out_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
