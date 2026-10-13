#!/usr/bin/env bash
set -euo pipefail
python -m cProfile -o stats.prof scripts/profile_entry.py
echo "Perfil guardado en stats.prof"
