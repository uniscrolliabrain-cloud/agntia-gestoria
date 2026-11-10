import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time

from fastapi.testclient import TestClient
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run the disposable Agente + Gestoría compatibility probe")
    parser.add_argument("--gestoria", type=Path, required=True, help="Checkout with a built TypeScript SDK")
    parser.add_argument("--agente", type=Path, required=True, help="Checkout with its locked dependencies installed")
    parser.add_argument("--baseline", action="store_true", help="Expect and reproduce the old agent case closure")
    args = parser.parse_args()
    checkout = args.gestoria.resolve()
    agente = args.agente.resolve()
    variant = "baseline" if args.baseline else "fixed"
    loader = agente / "node_modules/tsx/dist/loader.mjs"
    hono = agente / "node_modules/hono"
    if not loader.is_file() or not (hono / "package.json").is_file():
        parser.error("Install Agente's locked dependencies before running the probe")
    sys.path.insert(0, str(checkout))
    from agntia_gestoria.app import create_app

    with tempfile.TemporaryDirectory(prefix="gestoria-sdk-probe-") as directory:
        scratch = Path(directory)
        shutil.copytree(hono, scratch / "node_modules/hono")
        for filename in ("probe.mjs", "runtime-probe.mts"):
            shutil.copy2(Path(__file__).with_name(filename), scratch / filename)
        owner_token = secrets.token_hex(24)
        agent_token = secrets.token_hex(24)
        os.environ.update(
            GESTORIA_DATA_DIR=str(scratch / "data"), GESTORIA_OWNER_TOKEN=owner_token,
            GESTORIA_ACTORS_JSON="{}", ODOO_ADAPTER_ENABLED="false",
        )
        with TestClient(create_app()) as fixture:
            headers = {"Authorization": f"Bearer {owner_token}"}
            company_a, company_b = [
                fixture.post("/api/companies", headers=headers, json={"name": name, "legal_form": "autonomo"}).json()["id"]
                for name in ("Empresa sintética A", "Empresa sintética B")
            ]
        os.environ["GESTORIA_ACTORS_JSON"] = json.dumps({
            agent_token: {"id": "agent-a", "role": "agent", "companies": [company_a]},
        })
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            server = uvicorn.Server(uvicorn.Config(create_app(), log_level="warning"))
            thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
            thread.start()
            try:
                for _ in range(200):
                    if server.started:
                        break
                    if not thread.is_alive():
                        raise RuntimeError("Uvicorn terminated before readiness")
                    time.sleep(0.025)
                else:
                    raise RuntimeError("Uvicorn was not ready")
                subprocess.run(
                    ["node", "--import", loader.as_uri(), str(scratch / "probe.mjs")],
                    env={**os.environ, "GESTORIA_PROBE_URL": f"http://127.0.0.1:{listener.getsockname()[1]}",
                         "GESTORIA_PROBE_AGENT": agent_token, "GESTORIA_PROBE_OWNER": owner_token,
                         "GESTORIA_PROBE_A": company_a, "GESTORIA_PROBE_B": company_b,
                         "GESTORIA_PROBE_VARIANT": variant, "GESTORIA_PROBE_CHECKOUT": str(checkout),
                         "GESTORIA_PROBE_AGENTE": str(agente)},
                    check=True, timeout=90,
                )
            finally:
                server.should_exit = True
                thread.join(10)


if __name__ == "__main__":
    main()
