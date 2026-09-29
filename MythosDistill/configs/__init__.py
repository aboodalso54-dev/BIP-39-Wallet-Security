"""Central configuration for the Claude Mythos distillation pipeline.

All hyper-parameters, paths, and model identifiers live here so the scripts
can import them with ``from configs import ...``.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
ADAPTERS_DIR = os.path.join(BASE_DIR, "adapters")

for _d in (DATA_DIR, MODELS_DIR, OUTPUTS_DIR, ADAPTERS_DIR):
    os.makedirs(_d, exist_ok=True)

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
DATASET_ID = "WithinUsAI/claude_mythos_distilled_25k"
DATASET_CONFIG = "default"
DATASET_SPLIT_TRAIN = "train"
DATASET_SPLIT_VAL = "validation"
DATASET_SPLIT_TEST = "test"

# Category sizes (informational, used for curriculum weighting)
CATEGORY_SIZES: Dict[str, int] = {
    "cybersecurity": 7000,
    "advanced_coding": 5500,
    "agentic_planning": 3500,
    "general_expert_qa": 3500,
    "mathematical_reasoning": 3000,
    "scientific_analysis": 2500,
}

# ---------------------------------------------------------------------------
# Base model
# ---------------------------------------------------------------------------
BASE_MODEL_ID = "Qwen/Qwen2.5-1.5B"
BASE_MODEL_REVISION = "main"

# ---------------------------------------------------------------------------
# Tokenizer / chat template (Qwen3 style)
# ---------------------------------------------------------------------------
CHAT_TEMPLATE = (
    "{% for message in messages %}"
    "{% if message['role'] == 'system' %}"
    "<|im_start|>system\n{{ message['content'] }}<|im_end|>\n"
    "{% elif message['role'] == 'user' %}"
    "<|im_start|>user\n{{ message['content'] }}<|im_end|>\n"
    "{% elif message['role'] == 'assistant' %}"
    "<|im_start|>assistant\n{{ message['content'] }}<|im_end|>\n"
    "{% endif %}"
    "{% endfor %}"
)

# ---------------------------------------------------------------------------
# QLoRA adapters
# ---------------------------------------------------------------------------
LORA_R = 64
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES: List[str] = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]
LORA_TASK_TYPE = "CAUSAL_LM"

# Quantisation (4-bit NF4)
BNB_CONFIG_4BIT = dict(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype="float16",
)

# ---------------------------------------------------------------------------
# SFT training hyper-parameters (full run)
# ---------------------------------------------------------------------------
SFT_MAX_LENGTH = 2048
SFT_MAX_STEPS = 2000
SFT_LEARNING_RATE = 2e-4
SFT_WARMUP_STEPS = 100
SFT_LR_SCHEDULER_TYPE = "cosine"
SFT_GRADIENT_ACCUMULATION_STEPS = 4
SFT_PER_DEVICE_BATCH_SIZE = 2
SFT_PACKING = False
SFT_DATASET_TEXT_FIELD = "text"
SFT_NUM_TRAIN_EPOCHS: Optional[float] = None
SFT_WEIGHT_DECAY = 0.0
SFT_SEED = 42
SFT_EVAL_STRATEGY = "steps"
SFT_EVAL_STEPS = 100
SFT_SAVE_STRATEGY = "steps"
SFT_SAVE_STEPS = 500
SFT_LOGGING_STEPS = 20
SFT_REPORT_TO = ["tensorboard"]
SFT_OUTPUT_DIR = os.path.join(OUTPUTS_DIR, "sft_checkpoints")
SFT_OPTIMIZER = "paged_adamw_8bit"

# ---------------------------------------------------------------------------
# DPO training hyper-parameters
# ---------------------------------------------------------------------------
DPO_MAX_LENGTH = 1024
DPO_MAX_TARGET_LENGTH = 1024
DPO_BETA = 0.1
DPO_LEARNING_RATE = 5e-7
DPO_WARMUP_STEPS = 50
DPO_LR_SCHEDULER_TYPE = "cosine"
DPO_GRADIENT_ACCUMULATION_STEPS = 4
DPO_PER_DEVICE_BATCH_SIZE = 2
DPO_NUM_TRAIN_EPOCHS = 1
DPO_SEED = 42
DPO_OUTPUT_DIR = os.path.join(OUTPUTS_DIR, "dpo_checkpoints")
DPO_OPTIMIZER = "adamw_torch"
DPO_LABEL_SMOOTHING_EPS = 0.0
DPO_REFERENCE_FREE = False

# ---------------------------------------------------------------------------
# GGUF export
# ---------------------------------------------------------------------------
GGUF_OUTDIR = os.path.join(MODELS_DIR, "gguf")
GGUF_QUANT_TYPES = ["q4_K_M", "q8_0"]

# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
EVAL_MAX_NEW_TOKENS = 512
EVAL_BATCH_SIZE = 4
EVAL_SAMPLES = 50
EVAL_OUTDIR = os.path.join(OUTPUTS_DIR, "eval_results")

# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
INFER_MAX_NEW_TOKENS = 512
INFER_TEMPERATURE = 0.7
INFER_TOP_P = 0.9
INFER_REPETITION_PENALTY = 1.1
INFER_MAX_INPUT_LENGTH = 2048

# ---------------------------------------------------------------------------
# Smoke test defaults (small model, few examples)
# ---------------------------------------------------------------------------
SMOKE_MODEL_ID = "gpt2"
SMOKE_MAX_LENGTH = 256
SMOKE_EXAMPLES = 20
SMOKE_MAX_STEPS = 20
SMOKE_PER_DEVICE_BATCH_SIZE = 2
SMOKE_GRADIENT_ACCUMULATION_STEPS = 1
SMOKE_LEARNING_RATE = 2e-4
SMOKE_PACKING = False
SMOKE_DATASET_TEXT_FIELD = "text"
SMOKE_OUTDIR = os.path.join(OUTPUTS_DIR, "smoke_test")
SMOKE_SEED = 42