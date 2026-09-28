#!/usr/bin/env python3
"""08_inference.py - interactive inference demo with the merged model."""

from __future__ import annotations

import os
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (
    CHAT_TEMPLATE,
    INFER_MAX_INPUT_LENGTH,
    INFER_MAX_NEW_TOKENS,
    INFER_REPETITION_PENALTY,
    INFER_TEMPERATURE,
    INFER_TOP_P,
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


def main() -> None:
    model_dir = os.environ.get("MODEL_DIR", os.path.join(SFT_OUTPUT_DIR, "merged"))
    print(f"[infer] Loading model from {model_dir}")
    model, tokenizer = load_model(model_dir)

    print("[infer] Interactive mode. Type 'quit' to exit.")
    messages = []
    while True:
        user_input = input(">>> ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        messages.append({"role": "user", "content": user_input})

        inp = tokenizer.apply_chat_template(
            messages, return_tensors="pt", add_generation_prompt=True
        )
        try:
            input_ids = inp["input_ids"]
        except Exception:
            input_ids = inp
        input_ids = input_ids.to(model.device)

        with torch.no_grad():
            out = model.generate(
                input_ids=input_ids,
                max_new_tokens=INFER_MAX_NEW_TOKENS,
                temperature=INFER_TEMPERATURE,
                top_p=INFER_TOP_P,
                repetition_penalty=INFER_REPETITION_PENALTY,
                pad_token_id=tokenizer.eos_token_id,
            )
        gen = tokenizer.decode(out[0][input_ids.shape[-1]:], skip_special_tokens=True)
        print(f"<<< {gen}")
        messages.append({"role": "assistant", "content": gen})

        if len(messages) > 20:
            messages = messages[-20:]


if __name__ == "__main__":
    main()