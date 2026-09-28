#!/usr/bin/env python3
"""05_export_gguf.py - convert merged model to GGUF and quantize (q4_K_M, q8_0)."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import (
    BASE_MODEL_ID,
    CHAT_TEMPLATE,
    GGUF_OUTDIR,
    GGUF_QUANT_TYPES,
    SFT_OUTPUT_DIR,
)


def main() -> None:
    os.makedirs(GGUF_OUTDIR, exist_ok=True)

    merged_dir = os.environ.get("MERGED_DIR", os.path.join(SFT_OUTPUT_DIR, "merged"))
    out_path = os.path.join(GGUF_OUTDIR, "mythos.gguf")

    # Convert using the llama.cpp convert script (expected on PATH).
    convert_script = os.environ.get(
        "LLAMA_CONVERT_SCRIPT", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "convert_hf_to_gguf.py")
    )

    import subprocess

    cmd = [
        sys.executable,
        convert_script,
        "--model-dir",
        merged_dir,
        "--out-file",
        out_path,
        "--outtype",
        "f16",
    ]
    print(f"[gguf] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    for qtype in GGUF_QUANT_TYPES:
        quant_path = os.path.join(GGUF_OUTDIR, f"mythos-{qtype}.gguf")
        qcmd = ["llama-quantize", out_path, quant_path, qtype]
        print(f"[gguf] Quantizing -> {qtype}")
        try:
            subprocess.run(qcmd, check=True)
        except FileNotFoundError:
            print(f"[gguf] WARNING: llama-quantize not found; skipping {qtype}")
        except subprocess.CalledProcessError as e:
            print(f"[gguf] WARNING: quantize {qtype} failed: {e}")

    print(f"[gguf] Done. GGUF files in {GGUF_OUTDIR}")


if __name__ == "__main__":
    main()