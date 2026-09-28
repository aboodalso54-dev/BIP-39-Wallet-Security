#!/usr/bin/env python3
"""smoke_test.py - end-to-end test with GPT-2 on 20 examples."""

from __future__ import annotations

import os
import sys

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset, DatasetDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (
    CHAT_TEMPLATE,
    DATA_DIR,
    LORA_ALPHA,
    LORA_DROPOUT,
    LORA_R,
    LORA_TARGET_MODULES,
    SMOKE_DATASET_TEXT_FIELD,
    SMOKE_EXAMPLES,
    SMOKE_LEARNING_RATE,
    SMOKE_MAX_LENGTH,
    SMOKE_MAX_STEPS,
    SMOKE_OUTDIR,
    SMOKE_PACKING,
    SMOKE_PER_DEVICE_BATCH_SIZE,
    SMOKE_GRADIENT_ACCUMULATION_STEPS,
    SMOKE_MODEL_ID,
    SMOKE_SEED,
)

try:
    from trl import SFTConfig, SFTTrainer
except ImportError:  # pragma: no cover
    from transformers import TrainingArguments
    from trl import SFTTrainer
    SFTConfig = None  # type: ignore


def _format_messages(messages, tokenizer) -> str:
    """Convert a list of messages into a single chat-template string."""
    try:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
    except Exception:
        parts = []
        for m in messages:
            parts.append(f"{m['role']}: {m['content']}")
        return "\n".join(parts)


def _make_small_dataset(tokenizer) -> DatasetDict:
    """Create a tiny 20-example dataset for the smoke test."""
    raw_dir = os.path.join(DATA_DIR, "raw")
    if os.path.isdir(raw_dir):
        dsd = DatasetDict.load_from_disk(raw_dir)
        train = dsd["train"].select(range(min(SMOKE_EXAMPLES, len(dsd["train"]))))
        val = dsd["validation"].select(range(min(5, len(dsd["validation"]))))
    else:
        data = {
            "text": [
                f"Q: What is {i} + {i}? A: {i + i}" for i in range(SMOKE_EXAMPLES)
            ]
        }
        train = Dataset.from_dict(data)
        val = Dataset.from_dict({"text": data["text"][:5]})
        return DatasetDict({"train": train, "validation": val})

    # Convert messages -> text using the chat template
    train_text = [_format_messages(ex["messages"], tokenizer) for ex in train]
    val_text = [_format_messages(ex["messages"], tokenizer) for ex in val]
    train = Dataset.from_dict({"text": train_text})
    val = Dataset.from_dict({"text": val_text})
    return DatasetDict({"train": train, "validation": val})


def main() -> None:
    os.makedirs(SMOKE_OUTDIR, exist_ok=True)
    print(f"[smoke] Using model {SMOKE_MODEL_ID}")

    tokenizer = AutoTokenizer.from_pretrained(SMOKE_MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.chat_template = CHAT_TEMPLATE

    model = AutoModelForCausalLM.from_pretrained(SMOKE_MODEL_ID)

    # Wrap with LoRA for a quick parameter-efficient smoke test.
    # GPT-2 uses Conv1D layers named c_attn / c_proj / c_fc.
    gpt2_targets = ["c_attn", "c_proj", "c_fc"]
    peft_cfg = LoraConfig(
        r=min(LORA_R, 16),
        lora_alpha=LORA_ALPHA,
        target_modules=gpt2_targets,
        lora_dropout=0.0,
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_cfg)
    model.print_trainable_parameters()

    dsd = _make_small_dataset(tokenizer)
    print(f"[smoke] Train: {len(dsd['train'])} | Val: {len(dsd['validation'])}")

    if SFTConfig is not None:
        training_args = SFTConfig(
            output_dir=SMOKE_OUTDIR,
            max_length=SMOKE_MAX_LENGTH,
            packing=SMOKE_PACKING,
            dataset_text_field=SMOKE_DATASET_TEXT_FIELD,
            per_device_train_batch_size=SMOKE_PER_DEVICE_BATCH_SIZE,
            per_device_eval_batch_size=SMOKE_PER_DEVICE_BATCH_SIZE,
            gradient_accumulation_steps=SMOKE_GRADIENT_ACCUMULATION_STEPS,
            learning_rate=SMOKE_LEARNING_RATE,
            max_steps=SMOKE_MAX_STEPS,
            lr_scheduler_type="cosine",
            warmup_steps=0,
            eval_strategy="steps",
            eval_steps=10,
            save_strategy="no",
            logging_steps=5,
            report_to=[],
            seed=SMOKE_SEED,
            fp16=False,
            bf16=False,
        )
    else:  # pragma: no cover
        training_args = TrainingArguments(  # type: ignore[misc]
            output_dir=SMOKE_OUTDIR,
            per_device_train_batch_size=SMOKE_PER_DEVICE_BATCH_SIZE,
            per_device_eval_batch_size=SMOKE_PER_DEVICE_BATCH_SIZE,
            gradient_accumulation_steps=SMOKE_GRADIENT_ACCUMULATION_STEPS,
            learning_rate=SMOKE_LEARNING_RATE,
            max_steps=SMOKE_MAX_STEPS,
            eval_strategy="steps",
            eval_steps=10,
            save_strategy="no",
            logging_steps=5,
            report_to=[],
            seed=SMOKE_SEED,
        )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dsd["train"],
        eval_dataset=dsd["validation"],
        processing_class=tokenizer,
    )

    print("[smoke] Starting training ...")
    trainer.train()
    print("[smoke] Saving model ...")
    trainer.save_model(SMOKE_OUTDIR)
    tokenizer.save_pretrained(SMOKE_OUTDIR)
    print(f"[smoke] Done. Model saved to {SMOKE_OUTDIR}")

    # Quick generation test
    print("[smoke] Running generation test ...")
    msgs = [{"role": "user", "content": "What is 2 + 2?"}]
    tokens = tokenizer.apply_chat_template(msgs, return_tensors="pt", add_generation_prompt=True)
    # BatchEncoding may raise on isinstance checks in some transformers versions.
    try:
        input_ids = tokens["input_ids"]
    except Exception:
        input_ids = tokens
    with torch.no_grad():
        out = model.generate(
            input_ids=input_ids,
            max_new_tokens=32,
            pad_token_id=tokenizer.eos_token_id,
        )
    gen = tokenizer.decode(out[0][input_ids.shape[-1]:], skip_special_tokens=True)
    print(f"[smoke] Generated: {gen!r}")
    print("[smoke] Smoke test PASSED.")


if __name__ == "__main__":
    main()