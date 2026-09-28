#!/usr/bin/env python3
"""09_orchestrate.py - one-command pipeline runner."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import List

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(HERE)
VENV_PY = "/tmp/venv/bin/python"


def _run(script: str, extra: List[str] | None = None) -> None:
    path = os.path.join(HERE, script)
    cmd = [VENV_PY, path]
    if extra:
        cmd.extend(extra)
    print(f"\n=== Running: {' '.join(cmd)} ===")
    subprocess.run(cmd, check=True, cwd=BASE_DIR)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Mythos distillation pipeline")
    parser.add_argument(
        "steps",
        nargs="*",
        choices=["download", "preprocess", "smoke", "sft", "merge", "gguf", "dpo", "eval", "infer", "all"],
        default=["all"],
        help="Which steps to run (default: all)",
    )
    args = parser.parse_args()

    if "all" in args.steps:
        args.steps = ["download", "preprocess", "smoke", "sft", "merge", "gguf", "dpo", "eval", "infer"]

    for step in args.steps:
        if step == "download":
            _run("01_download_dataset.py")
        elif step == "preprocess":
            _run("02_preprocess.py")
        elif step == "smoke":
            _run("smoke_test.py")
        elif step == "sft":
            _run("03_train_sft.py")
        elif step == "merge":
            _run("04_merge_lora.py")
        elif step == "gguf":
            _run("05_export_gguf.py")
        elif step == "dpo":
            _run("06_train_dpo.py")
        elif step == "eval":
            _run("07_evaluate.py")
        elif step == "infer":
            _run("08_inference.py")

    print("\n=== Pipeline complete ===")


if __name__ == "__main__":
    main()