import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_inventory():
    result = subprocess.run(
        [sys.executable, "scripts/baseline_inventory.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


class BaselineInventory(unittest.TestCase):
    """C00: el baseline debe ser reproducible, no una afirmación del README."""

    def test_frozen_baseline_reports_pass(self):
        data = run_inventory()
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["frozen_baseline"]["status"], "PASS")
        self.assertEqual(data["frozen_baseline"]["verified_files"], 43)
        self.assertGreaterEqual(data["tracked_files"], 100)

    def test_inventory_is_reproducible(self):
        self.assertEqual(run_inventory(), run_inventory())

    def test_every_test_module_is_listed(self):
        data = run_inventory()
        on_disk = {path.name for path in (ROOT / "tests").glob("test_*.py")}
        self.assertEqual(set(data["tests"]["names"]), on_disk)
        self.assertIn("test_baseline.py", data["tests"]["names"])
        self.assertEqual(data["tests"]["files"], len(on_disk))

    def test_ci_runs_the_unittest_suite(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("unittest discover", workflow)
        self.assertIn("verify_baseline", workflow)

    def test_only_placeholder_env_files_are_tracked(self):
        files = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.split()
        env_like = [name for name in files if name.split("/")[-1].startswith(".env") or name.endswith("env.example")]
        self.assertTrue(env_like, "el inventario debe contener al menos una plantilla de entorno")
        self.assertTrue(all(name.endswith(".example") for name in env_like), env_like)
