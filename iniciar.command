#!/bin/zsh
set -eu
cd "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  print -u2 "Falta .venv. Consulta README.md para recrear el entorno."
  exit 1
fi
exec .venv/bin/python -c '
import os, runpy, sys
from dotenv import load_dotenv
load_dotenv(".env")
if not os.environ.get("GOOGLE_API_KEY"):
    sys.exit("Falta GOOGLE_API_KEY. Configúrala en .env y vuelve a abrir iniciar.command.")
runpy.run_path("app.py", run_name="__main__")
'
