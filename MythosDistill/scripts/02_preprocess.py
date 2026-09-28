#!/usr/bin/env python3
"""02_preprocess.py - quality filters, curriculum weighting, chat template, save as Arrow."""

from __future__ import annotations

import os
import re
import sys
from collections import Counter
from typing import Dict, List

# Ensure /tmp is writable for any temp files used by libraries.
os.environ.setdefault("TMPDIR", "/tmp")
os.environ.setdefault("DATASETS_NUM_PROC", "1")

from datasets import Dataset, DatasetDict, load_dataset

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (
    BASE_DIR,
    CHAT_TEMPLATE,
    CATEGORY_SIZES,
    DATA_DIR,
    DATASET_SPLIT_TEST,
    DATASET_SPLIT_TRAIN,
    DATASET_SPLIT_VAL,
)

VALID_ROLES = {"system", "user", "assistant"}
MIN_CONTENT_LEN = 8
MAX_CONTENT_LEN = 8192
ESCAPE_HATCH_PATTERNS = [
    re.compile(r"ignore (all )?previous instructions", re.IGNORECASE),
    re.compile(r"disregard (all )?previous instructions", re.IGNORECASE),
    re.compile(r"you are now\b", re.IGNORECASE),
    re.compile(r"new instructions?:", re.IGNORECASE),
    re.compile(r"\[INST\]", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"system prompt", re.IGNORECASE),
]

CURRICULUM_WEIGHTS: Dict[str, float] = {
    "cybersecurity": 1.2,
    "advanced_coding": 1.15,
    "agentic_planning": 1.1,
    "general_expert_qa": 1.0,
    "mathematical_reasoning": 1.25,
    "scientific_analysis": 1.3,
}


def _has_escape_hatch(content: str) -> bool:
    return any(p.search(content) for p in ESCAPE_HATCH_PATTERNS)


def _validate_messages(messages: List[Dict]) -> bool:
    if not messages:
        return False
    for msg in messages:
        if not isinstance(msg, dict):
            return False
        role = msg.get("role")
        content = msg.get("content")
        if role not in VALID_ROLES:
            return False
        if not isinstance(content, str):
            return False
        if len(content.strip()) < MIN_CONTENT_LEN:
            return False
        if len(content) > MAX_CONTENT_LEN:
            return False
        if _has_escape_hatch(content):
            return False
    return True


def _curriculum_weight(category: str) -> float:
    return CURRICULUM_WEIGHTS.get(category, 1.0)


def _manual_filter(ds: Dataset) -> Dataset:
    """Filter a dataset in pure Python (no multiprocessing) to avoid
    semaphore issues in restricted containers."""
    print(f"[preprocess] Filtering {len(ds)} examples ...")
    keep = []
    for i in range(len(ds)):
        example = ds[i]
        if _validate_messages(example.get("messages", [])):
            keep.append(i)
    print(f"[preprocess] Keeping {len(keep)} / {len(ds)} examples")
    if len(keep) == len(ds):
        return ds
    return ds.select(keep)


def main() -> None:
    raw_dir = os.path.join(DATA_DIR, "raw")
    print(f"[preprocess] Loading raw dataset from {raw_dir}")
    dsd = DatasetDict.load_from_disk(raw_dir)

    processed = {}
    for split in (DATASET_SPLIT_TRAIN, DATASET_SPLIT_VAL, DATASET_SPLIT_TEST):
        ds = dsd[split]
        print(f"[preprocess] Processing {split}: {len(ds)} examples")
        ds = _manual_filter(ds)
        print(f"[preprocess] {split} after filter: {len(ds)}")

        if "category" in ds.column_names:
            ds = ds.add_column(
                "weight",
                [_curriculum_weight(c) for c in ds["category"]],
            )

        processed[split] = ds

    out_dir = os.path.join(DATA_DIR, "processed")
    out = DatasetDict(processed)
    out.save_to_disk(out_dir)
    print(f"[preprocess] Saved processed dataset to {out_dir}")

    train = processed[DATASET_SPLIT_TRAIN]
    if "category" in train.column_names:
        counts = Counter(train["category"])
        print(f"[preprocess] Train category distribution: {dict(counts)}")


if __name__ == "__main__":
    main()