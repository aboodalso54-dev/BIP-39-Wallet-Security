# Claude Mythos Distillation Pipeline

A production-ready pipeline to distill the synthetic 25K `WithinUsAI/claude_mythos_distilled_25k`
dataset (Apache 2.0) into a smaller, faster model using QLoRA SFT + optional DPO, then export to GGUF.

## Directory Layout

```
MythosDistill/
├── configs/             # All hyper-parameters, paths, model IDs
├── scripts/             # 01_download .. 09_orchestrate + smoke_test.py
├── react-native/        # OllamaClient.ts (React Native HTTP client)
├── data/                # Downloaded + processed Arrow datasets
├── models/              # GGUF outputs
├── adapters/            # LoRA adapter checkpoints
└── outputs/             # Training checkpoints, eval results
```

## Setup

```bash
python3 -m venv /tmp/venv
/tmp/venv/bin/pip install -r requirements.txt
```

## Quick Start (Smoke Test)

```bash
/tmp/venv/bin/python scripts/09_orchestrate.py smoke
```

This runs GPT-2 on 20 examples to validate the full training pipeline end-to-end.

## Full Pipeline

```bash
/tmp/venv/bin/python scripts/09_orchestrate.py all
```

Runs: download → preprocess → smoke → SFT → merge → GGUF → DPO → eval → infer.

## Individual Steps

| Script | Description |
| --- | --- |
| `01_download_dataset.py` | Download 25K dataset, split train/val/test |
| `02_preprocess.py` | Quality filters, curriculum weighting, chat template, save Arrow |
| `03_train_sft.py` | QLoRA SFT on Qwen3-8B with TRL SFTTrainer + SFTConfig |
| `04_merge_lora.py` | Merge LoRA adapter into base model |
| `05_export_gguf.py` | Convert to GGUF, quantize q4_K_M / q8_0 |
| `06_train_dpo.py` | DPO preference optimization |
| `07_evaluate.py` | MT-Bench, HumanEval, GSM8K benchmarks |
| `08_inference.py` | Interactive inference demo |
| `smoke_test.py` | End-to-end test with GPT-2 on 20 examples |

## React Native Client

Use `OllamaClient` from `react-native/OllamaClient.ts` to talk to a local Ollama server:

```ts
import OllamaClient, { defaultOllamaClient } from './MythosDistill/react-native/OllamaClient';

const res = await defaultOllamaClient.chat({
  model: 'mythos-q4_K_M',
  messages: [{ role: 'user', content: 'Hello!' }],
});

// Streaming
await defaultOllamaClient.chatStream(
  { model: 'mythos-q4_K_M', messages: [...] },
  (chunk) => console.log(chunk.message.content),
);
```

## Configuration

All parameters live in `configs/__init__.py`. Override via environment variables
or edit the constants directly.

## Requirements

See `requirements.txt`. Requires CUDA-capable GPU for full training runs.
Smoke test runs on CPU with GPT-2.