#!/usr/bin/env python3
"""07_evaluate.py - MT-Bench, HumanEval, GSM8K benchmarks."""

from __future__ import annotations

import json
import os
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (
    CHAT_TEMPLATE,
    EVAL_BATCH_SIZE,
    EVAL_MAX_NEW_TOKENS,
    EVAL_OUTDIR,
    EVAL_SAMPLES,
    SFT_OUTPUT_DIR,
)


def load_model(model_dir: str):
    tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    tokenizer.chat_template = CHAT_TEMPLATE
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    return model, tokenizer


def mtbench(model, tokenizer, out_path: str) -> None:
    """Lightweight MT-Bench: single-turn Q&A scoring placeholder."""
    questions = [
        "Explain quantum entanglement in simple terms.",
        "Write a Python function to check if a number is prime.",
        "What are the ethical implications of AI in healthcare?",
    ]
    results = []
    for q in questions:
        msgs = [{"role": "user", "content": q}]
        tokens = tokenizer.apply_chat_template(msgs, return_tensors="pt", add_generation_prompt=True)
        try:
            input_ids = tokens["input_ids"]
        except Exception:
            input_ids = tokens
        with torch.no_grad():
            out = model.generate(
                input_ids=input_ids,
                max_new_tokens=EVAL_MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        gen = tokenizer.decode(out[0][input_ids.shape[-1]:], skip_special_tokens=True)
        results.append({"question": q, "answer": gen})
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[eval] MT-Bench results written to {out_path}")


defhumaneval(model, tokenizer, out_path: str) -> None:
    """HumanEval: run the first 10 tasks from the HumanEval dataset."""
    from datasets import load_dataset

    ds = load_dataset("openai/humaneval", split="test")
    results = []
    for i, ex in enumerate(ds):
        if i >= 10:
            break
        prompt = ex["prompt"]
        msgs = [{"role": "user", "content": prompt}]
        tokens = tokenizer.apply_chat_template(msgs, return_tensors="pt", add_generation_prompt=True)
        try:
            input_ids = tokens["input_ids"]
        except Exception:
            input_ids = tokens
        with torch.no_grad():
            out = model.generate(
                input_ids=input_ids,
                max_new_tokens=EVAL_MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        gen = tokenizer.decode(out[0][input_ids.shape[-1]:], skip_special_tokens=True)
        results.append({"task_id": ex["task_id"], "prompt": prompt, "completion": gen})
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[eval] HumanEval results written to {out_path}")


def gsm8k(model, tokenizer, out_path: str) -> None:
    """GSM8K: run a small subset."""
    from datasets import load_dataset

    ds = load_dataset("gsm8k", "main", split="test")
    results = []
    for i, ex in enumerate(ds):
        if i >= EVAL_SAMPLES:
            break
        msgs = [{"role": "user", "content": ex["question"]}]
        tokens = tokenizer.apply_chat_template(msgs, return_tensors="pt", add_generation_prompt=True)
        try:
            input_ids = tokens["input_ids"]
        except Exception:
            input_ids = tokens
        with torch.no_grad():
            out = model.generate(
                input_ids=input_ids,
                max_new_tokens=EVAL_MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        gen = tokenizer.decode(out[0][input_ids.shape[-1]:], skip_special_tokens=True)
        results.append({"question": ex["question"], "answer": gen, "expected": ex["answer"]})
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[eval] GSM8K results written to {out_path}")


def main() -> None:
    os.makedirs(EVAL_OUTDIR, exist_ok=True)
    model_dir = os.environ.get("MODEL_DIR", os.path.join(SFT_OUTPUT_DIR, "merged"))
    print(f"[eval] Loading model from {model_dir}")
    model, tokenizer = load_model(model_dir)

    mtbench(model, tokenizer, os.path.join(EVAL_OUTDIR, "mtbench.json"))
    humaneval(model, tokenizer, os.path.join(EVAL_OUTDIR, "humaneval.json"))
    gsm8k(model, tokenizer, os.path.join(EVAL_OUTDIR, "gsm8k.json"))
    print("[eval] All benchmarks complete.")


if __name__ == "__main__":
    main()