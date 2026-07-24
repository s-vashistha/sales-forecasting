#!/usr/bin/env bash
# Render build script
set -e

echo "=== Step 1: Upgrade pip ==="
pip install --upgrade pip

echo "=== Step 2: Install dependencies ==="
pip install -r requirements.txt

echo "=== Build complete ==="
