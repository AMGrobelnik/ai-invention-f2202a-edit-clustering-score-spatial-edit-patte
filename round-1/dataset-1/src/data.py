#!/usr/bin/env python3
"""Convert Wikipedia text-pair dataset to exp_sel_data_out schema."""

import json
import sys
from pathlib import Path

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

WORKSPACE = Path(__file__).parent


@logger.catch(reraise=True)
def main():
    src = WORKSPACE / "data_out.json"
    logger.info(f"Loading {src}")
    pairs = json.loads(src.read_text())
    logger.info(f"Loaded {len(pairs)} pairs")

    examples = []
    for pair in pairs:
        # input: JSON string with both texts and metadata
        inp = json.dumps({
            "text_a": pair["text_a"],
            "text_b": pair["text_b"],
        })
        # output: label
        out = pair["label"]

        example = {
            "input": inp,
            "output": out,
            "metadata_pair_id": pair["pair_id"],
            "metadata_fold": pair["fold"],
            "metadata_label": pair["label"],
            "metadata_jaccard_5gram": pair["jaccard_5gram"],
            "metadata_word_count_a": pair["word_count_a"],
            "metadata_word_count_b": pair["word_count_b"],
            "metadata_category": pair["category"],
            "metadata_task_type": "classification",
            "metadata_n_classes": 3,
        }
        if pair.get("splice_start_pct") is not None:
            example["metadata_splice_start_pct"] = pair["splice_start_pct"]
            example["metadata_splice_length_pct"] = pair["splice_length_pct"]
        examples.append(example)

    full_data = {
        "metadata": {
            "source": "Wikipedia text pairs (synthetic)",
            "description": "900 labeled text pairs: near_duplicate (splice edit), hard_negative (same category), random (different categories)",
            "n_pairs": len(examples),
            "classes": ["near_duplicate", "hard_negative", "random"],
        },
        "datasets": [
            {
                "dataset": "wikipedia_text_pairs",
                "examples": examples,
            }
        ],
    }

    out_path = WORKSPACE / "full_data_out.json"
    out_path.write_text(json.dumps(full_data, indent=2))
    logger.info(f"Wrote {out_path} with {len(examples)} examples")


if __name__ == "__main__":
    main()
