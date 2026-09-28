#!/usr/bin/env python3
"""01_download_dataset.py

Download the WithinUsAI/claude_mythos_distilled_25k dataset from HuggingFace,
split it into train / validation / test, and persist to disk as Arrow files.

Usage:
    python scripts/01_download_dataset.py
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Tuple

from datasets import Dataset, DatasetDict, load_dataset

# Make ``configs`` importable when running as ``python scripts/01_download_dataset.py``.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (  # noqa: E402
    DATA_DIR,
    DATASET_CONFIG,
    DATASET_ID,
    DATASET_SPLIT_TEST,
    DATASET_SPLIT_TRAIN,
    DATASET_SPLIT_VAL,
)

# Reproducible split.
SEED = 42
TEST_FRACTION = 0.05
VAL_FRACTION = 0.05


def _split_dataset(ds: Dataset) -> Tuple[Dataset, Dataset, Dataset]:
    """Split a HuggingFace ``Dataset`` into train / val / test deterministically."""
    train_test = ds.train_test_split(
        test_size=TEST_FRACTION + VAL_FRACTION,
        seed=SEED,
    )
    train: Dataset = train_test["train"]
    heldout: Dataset = train_test["test"]

    val_test = heldout.train_test_split(
        test_size=TEST_FRACTION / (TEST_FRACTION + VAL_FRACTION),
        seed=SEED,
    )
    val: Dataset = val_test["train"]
    test: Dataset = val_test["test"]
    return train, val, test


def main() -> None:
    print(f"[download] Loading dataset '{DATASET_ID}' (config={DATASET_CONFIG}) ...")
    ds = load_dataset(DATASET_ID, DATASET_CONFIG, split=DATASET_SPLIT_TRAIN)

    print(f"[download] Raw examples: {len(ds)}")
    print(f"[download] Columns: {ds.column_names}")

    train, val, test = _split_dataset(ds)
    print(
        f"[download] Splits -> train={len(train)} "
        f"val={len(val)} test={len(test)}"
    )

    out = DatasetDict(
        {
            DATASET_SPLIT_TRAIN: train,
            DATASET_SPLIT_VAL: val,
            DATASET_SPLIT_TEST: test,
        }
    )

    out_dir = os.path.join(DATA_DIR, "raw")
    out.save_to_disk(out_dir)
    print(f"[download] Saved Arrow dataset to {out_dir}")


if __name__ == "__main__":
    main()