#!/usr/bin/env python3
"""03_train_sft.py - QLoRA SFT on Qwen3-8B using TRL SFTTrainer + SFTConfig."""

from __future__ import annotations

import os
import sys

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (
    BNB_CONFIG_4BIT,
    CHAT_TEMPLATE,
    DATA_DIR,
    DATASET_SPLIT_TEST,
    DATASET_SPLIT_TRAIN,
    DATASET_SPLIT_VAL,
    LORA_ALPHA,
    LORA_DROPOUT,
    LORA_R,
    LORA_TARGET_MODULES,
    SFT_DATASET_TEXT_FIELD,
    SFT_EVAL_STEPS,
    SFT_EVAL_STRATEGY,
    SFT_GRADIENT_ACCUMULATION_STEPS,
    SFT_LEARNING_RATE,
    SFT_LOGGING_STEPS,
    SFT_MAX_LENGTH,
    SFT_NUM_TRAIN_EPOCHS,
    SFT_OPTIMIZER,
    SFT_OUTPUT_DIR,
    SFT_PACKING,
    SFT_PER_DEVICE_BATCH_SIZE,
    SFT_REPORT_TO,
    SFT_SAVE_STEPS,
    SFT_SAVE_STRATEGY,
    SFT_SEED,
    SFT_WARMUP_STEPS,
    SFT_WEIGHT_DECAY,
    SFT_MAX_STEPS,
    BASE_MODEL_ID,
)

try:
    from trl import SFTConfig, SFTTrainer
except ImportError:  # pragma: no cover - older trl fallback
    from transformers import TrainingArguments
    from trl import SFTTrainer

    SFTConfig = None  # type: ignore


def build_tokenizer(model_id: str):
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.chat_template = CHAT_TEMPLATE
    return tok


def build_model(model_id: str):
    bnb = BitsAndBytesConfig(**BNB_CONFIG_4BIT)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    peft_cfg = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=LORA_TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_cfg)
    model.print_trainable_parameters()
    return model


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


def _prepare_dataset(dsd, tokenizer):
    """Add a 'text' column to the dataset using the chat template."""
    from datasets import DatasetDict

    out = {}
    for split_name, ds in dsd.items():
        if "text" in ds.column_names:
            out[split_name] = ds
            continue
        texts = [_format_messages(ex["messages"], tokenizer) for ex in ds]
        ds = ds.add_column("text", texts)
        out[split_name] = ds
    return DatasetDict(out)


def main() -> None:
    os.makedirs(SFT_OUTPUT_DIR, exist_ok=True)
    tokenizer = build_tokenizer(BASE_MODEL_ID)
    model = build_model(BASE_MODEL_ID)

    from datasets import DatasetDict

    dsd = DatasetDict.load_from_disk(os.path.join(DATA_DIR, "processed"))
    dsd = _prepare_dataset(dsd, tokenizer)

    if SFTConfig is not None:
        training_args = SFTConfig(
            output_dir=SFT_OUTPUT_DIR,
            max_length=SFT_MAX_LENGTH,
            packing=SFT_PACKING,
            dataset_text_field=SFT_DATASET_TEXT_FIELD,
            per_device_train_batch_size=SFT_PER_DEVICE_BATCH_SIZE,
            per_device_eval_batch_size=SFT_PER_DEVICE_BATCH_SIZE,
            gradient_accumulation_steps=SFT_GRADIENT_ACCUMULATION_STEPS,
            learning_rate=SFT_LEARNING_RATE,
            warmup_steps=SFT_WARMUP_STEPS,
            lr_scheduler_type=SFT_LR_SCHEDULER_TYPE,
            weight_decay=SFT_WEIGHT_DECAY,
            max_steps=SFT_MAX_STEPS,
            num_train_epochs=SFT_NUM_TRAIN_EPOCHS or 1.0,
            eval_strategy=SFT_EVAL_STRATEGY,
            eval_steps=SFT_EVAL_STEPS,
            save_strategy=SFT_SAVE_STRATEGY,
            save_steps=SFT_SAVE_STEPS,
            logging_steps=SFT_LOGGING_STEPS,
            report_to=SFT_REPORT_TO,
            optim=SFT_OPTIMIZER,
            seed=SFT_SEED,
            load_in_4bit=True,
            bf16=False,
            fp16=True,
        )
    else:  # pragma: no cover
        training_args = TrainingArguments(  # type: ignore[misc]
            output_dir=SFT_OUTPUT_DIR,
            per_device_train_batch_size=SFT_PER_DEVICE_BATCH_SIZE,
            per_device_eval_batch_size=SFT_PER_DEVICE_BATCH_SIZE,
            gradient_accumulation_steps=SFT_GRADIENT_ACCUMULATION_STEPS,
            learning_rate=SFT_LEARNING_RATE,
            warmup_steps=SFT_WARMUP_STEPS,
            lr_scheduler_type=SFT_LR_SCHEDULER_TYPE,
            weight_decay=SFT_WEIGHT_DECAY,
            max_steps=SFT_MAX_STEPS,
            num_train_epochs=SFT_NUM_TRAIN_EPOCHS or 1.0,
            eval_strategy=SFT_EVAL_STRATEGY,
            eval_steps=SFT_EVAL_STEPS,
            save_strategy=SFT_SAVE_STRATEGY,
            save_steps=SFT_SAVE_STEPS,
            logging_steps=SFT_LOGGING_STEPS,
            report_to=SFT_REPORT_TO,
            optim=SFT_OPTIMIZER,
            seed=SFT_SEED,
            fp16=True,
        )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dsd[DATASET_SPLIT_TRAIN],
        eval_dataset=dsd[DATASET_SPLIT_VAL],
        processing_class=tokenizer,
    )

    print("[sft] Starting training ...")
    trainer.train()
    print("[sft] Saving final model ...")
    trainer.save_model(SFT_OUTPUT_DIR)
    tokenizer.save_pretrained(SFT_OUTPUT_DIR)
    print(f"[sft] Done. Model saved to {SFT_OUTPUT_DIR}")


if __name__ == "__main__":
    main()