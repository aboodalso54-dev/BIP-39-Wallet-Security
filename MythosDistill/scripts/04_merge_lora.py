#!/usr/bin/env python3
"""04_merge_lora.py - merge LoRA adapter into base model and save to disk."""

from __future__ import annotations

import os
import sys

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (
    BASE_MODEL_ID,
    CHAT_TEMPLATE,
    LORA_R,
    LORA_ALPHA,
    LORA_TARGET_MODULES,
    SFT_OUTPUT_DIR,
)


def main() -> None:
    adapter_dir = os.environ.get("ADAPTER_DIR", SFT_OUTPUT_DIR)
    out_dir = os.environ.get("MERGED_OUT", os.path.join(SFT_OUTPUT_DIR, "merged"))
    os.makedirs(out_dir, exist_ok=True)

    print(f"[merge] Loading base model {BASE_MODEL_ID} ...")
    base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    print(f"[merge] Loading LoRA adapter from {adapter_dir} ...")
    peft_model = PeftModel.from_pretrained(base, adapter_dir)

    print("[merge] Merging adapter into base ...")
    merged = peft_model.merge_and_unload()

    print(f"[merge] Saving merged model to {out_dir} ...")
    merged.save_pretrained(out_dir)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, trust_remote_code=True)
    tokenizer.chat_template = CHAT_TEMPLATE
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    tokenizer.save_pretrained(out_dir)
    print(f"[merge] Done. Merged model saved to {out_dir}")


if __name__ == "__main__":
    main()