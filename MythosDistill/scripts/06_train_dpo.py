#!/usr/bin/env python3
"""06_train_dpo.py - DPO preference optimization on the merged model."""

from __future__ import annotations

import os
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (
    CHAT_TEMPLATE,
    DPO_BETA,
    DPO_GRADIENT_ACCUMULATION_STEPS,
    DPO_LEARNING_RATE,
    DPO_LOGGING_STEPS,
    DPO_MAX_LENGTH,
    DPO_MAX_TARGET_LENGTH,
    DPO_NUM_TRAIN_EPOCHS,
    DPO_OPTIMIZER,
    DPO_OUTPUT_DIR,
    DPO_PER_DEVICE_BATCH_SIZE,
    DPO_REPORT_TO,
    DPO_SAVE_STEPS,
    DPO_SEED,
    DPO_WARMUP_STEPS,
    SFT_OUTPUT_DIR,
)


def main() -> None:
    os.makedirs(DPO_OUTPUT_DIR, exist_ok=True)
    merged_dir = os.environ.get("MERGED_DIR", os.path.join(SFT_OUTPUT_DIR, "merged"))

    tokenizer = AutoTokenizer.from_pretrained(merged_dir, trust_remote_code=True)
    tokenizer.chat_template = CHAT_TEMPLATE
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        merged_dir,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    ref_model = AutoModelForCausalLM.from_pretrained(
        merged_dir,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    from datasets import DatasetDict

    from trl import DPOConfig, DPOTrainer

    dsd = DatasetDict.load_from_disk(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed"))

    args = DPOConfig(
        output_dir=DPO_OUTPUT_DIR,
        beta=DPO_BETA,
        learning_rate=DPO_LEARNING_RATE,
        lr_scheduler_type="cosine",
        warmup_steps=DPO_WARMUP_STEPS,
        per_device_train_batch_size=DPO_PER_DEVICE_BATCH_SIZE,
        per_device_eval_batch_size=DPO_PER_DEVICE_BATCH_SIZE,
        gradient_accumulation_steps=DPO_GRADIENT_ACCUMULATION_STEPS,
        max_length=DPO_MAX_LENGTH,
        max_target_length=DPO_MAX_TARGET_LENGTH,
        num_train_epochs=DPO_NUM_TRAIN_EPOCHS,
        optim=DPO_OPTIMIZER,
        save_strategy="steps",
        save_steps=DPO_SAVE_STEPS,
        logging_steps=DPO_LOGGING_STEPS,
        report_to=DPO_REPORT_TO,
        seed=DPO_SEED,
        fp16=True,
    )

    trainer = DPOTrainer(
        model=model,
        ref_model=ref_model,
        args=args,
        processing_class=tokenizer,
        train_dataset=dsd["train"],
        eval_dataset=dsd["validation"],
    )

    print("[dpo] Starting DPO training ...")
    trainer.train()
    print("[dpo] Saving model ...")
    trainer.save_model(DPO_OUTPUT_DIR)
    tokenizer.save_pretrained(DPO_OUTPUT_DIR)
    print(f"[dpo] Done. Model saved to {DPO_OUTPUT_DIR}")


if __name__ == "__main__":
    main()