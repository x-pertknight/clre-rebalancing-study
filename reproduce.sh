#!/usr/bin/env bash
# Offline reproduction: sanity tests, gate on the archived runs, PDF number check.
# Exits non zero on any failure or mismatch. Run from anywhere; it cds to the repo root.
set -euo pipefail
cd "$(dirname "$0")"

# python3 -I ignores the script directory and PYTHONPATH, so put the repo root
# on sys.path explicitly before running each script (they import clre.py).
run() {
  python3 -I -c 'import os, runpy, sys; sys.path.insert(0, os.getcwd()); runpy.run_path(sys.argv[1], run_name="__main__")' "$1"
}

command -v pdftotext >/dev/null || { echo "pdftotext not found (install poppler)"; exit 1; }

echo "== tests.py"
run tests.py

echo "== reproduce_gate.py"
gate_out=$(run reproduce_gate.py)
echo "$gate_out"
# The headline break even values for the +-5% threshold policy, windows A, B, B'.
for be in "111.6%" "125.5%" "108.0%"; do
  grep -q "PASS  Threshold ±5%      BE  *${be}" <<<"$gate_out" || { echo "missing gate value $be"; exit 1; }
done
# The gate rewrites runs/gate003.json; it must match the committed file byte for byte.
if command -v git >/dev/null && git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --exit-code -- runs/gate003.json
fi

echo "== check_numbers.py"
run check_numbers.py

echo "reproduce.sh: all checks passed"
