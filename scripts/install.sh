#!/usr/bin/env bash
# Instalación local reproducible. No toca producción ni pide credenciales reales.
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"
VENV="${VENV:-.venv}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Falta $PYTHON. Instala Python 3.11 o superior." >&2
  exit 1
fi

"$PYTHON" -m venv "$VENV"
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet -e ".[dev]"

if [ ! -f .env ]; then
  cp env.example .env
  echo "Creado .env desde env.example: revisa los tokens antes de arrancar."
fi

echo
echo "Listo. Comandos:"
echo "  $VENV/bin/python -m pytest -q          # pruebas"
echo "  $VENV/bin/python -m agntia_gestoria.cli # servicio (según tu cli)"
echo
echo "Laboratorio opcional (Docker):"
echo "  docker compose -f docker-compose.lab.yml up -d"
echo "  docker compose -f docker-compose.lab.yml --profile odoo up -d"
