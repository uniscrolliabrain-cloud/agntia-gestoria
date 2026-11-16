"""Inventario reproducible del baseline (campaña C00).

Emite un JSON estable con SHA, rama, inventario congelado y matriz de tests.
No incluye timestamps a propósito: dos ejecuciones sobre el mismo árbol deben
producir el mismo documento para que la prueba de reproducibilidad tenga sentido.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)


def inventory():
    commit = _run("git", "rev-parse", "HEAD").stdout.strip()
    branch = _run("git", "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    dirty = bool(_run("git", "status", "--short").stdout.strip())
    tracked = [line for line in _run("git", "ls-files").stdout.splitlines() if line]
    baseline = _run(sys.executable, "scripts/verify_baseline.py")
    try:
        frozen = json.loads(baseline.stdout.strip() or "{}")
    except json.JSONDecodeError:
        frozen = {"status": "UNREADABLE"}
    tests = sorted(path.name for path in (ROOT / "tests").glob("test_*.py"))
    return {
        "schema_version": 1,
        "commit": commit,
        "branch": branch,
        "dirty": dirty,
        "tracked_files": len(tracked),
        "tests": {"files": len(tests), "names": tests},
        "frozen_baseline": frozen,
    }


def main():
    json.dump(inventory(), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
