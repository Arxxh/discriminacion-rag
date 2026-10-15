#!/bin/zsh
set -eu
cd "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  print -u2 "Falta .venv. Consulta README.md."
  exit 1
fi
exec .venv/bin/python debug_ollama/ejecutar.py --project "$PWD" "$@"
