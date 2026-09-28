#!/bin/bash
mkdir -p /root/.local/bin
ln -sf /home/agent_8ce4904f-9e8d-4a90-8e23-f3cb974600c2/openclaw/openclaw.mjs /root/.local/bin/openclaw
chmod +x /root/.local/bin/openclaw
/root/.local/bin/openclaw --version