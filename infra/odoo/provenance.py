"""Compare the installed package with source hashes from the C02 lock."""

import hashlib
from importlib.util import find_spec
import json
from pathlib import Path
import sys


def compare(lock, package_root):
    counts = {"match": 0, "different": 0, "missing": 0}
    for source in lock["sources"]:
        if source["repository"] != lock["upstream"]["repository"]:
            continue
        path = source["path"]
        if not path.startswith(("odoo/", "addons/")):
            continue
        relative = path.removeprefix("odoo/")
        installed = package_root / relative
        if not installed.is_file():
            result = "missing"
        elif hashlib.sha256(installed.read_bytes()).hexdigest() == source["sha256"]:
            result = "match"
        else:
            result = "different"
        counts[result] += 1
        print(f"{path}: {result}")
    if counts["match"] + counts["different"] == 0:
        raise RuntimeError("No locked source files could be compared to the installed package")
    print(json.dumps({"compared_source_files": counts, "full_package_equivalence": "NOT VERIFIED"}))


if __name__ == "__main__":
    root = Path(next(iter(find_spec("odoo").submodule_search_locations)))
    compare(json.load(sys.stdin), root)
