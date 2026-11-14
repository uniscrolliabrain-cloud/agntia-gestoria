# Atajos de desarrollo. Requiere make (Linux, macOS, WSL o Git Bash).
PYTHON ?= python3
VENV ?= .venv
COMPOSE ?= docker-compose.lab.yml

.PHONY: install test lab-up lab-odo lab-down connector-check security-digest

install:
	bash scripts/install.sh

test:
	$(VENV)/bin/python -m pytest -q

lab-up:
	docker compose -f $(COMPOSE) up -d

lab-odo:
	docker compose -f $(COMPOSE) --profile odoo up -d

lab-down:
	docker compose -f $(COMPOSE) --profile odoo down

# El conector TypeScript no tiene dependencias instaladas por defecto: solo comprueba el manifiesto.
connector-check:
	node -e "const p=require('./integrations/agente/package.json');console.log(p.name, p.version, 'ok')"

security-digest:
	curl -fsS -H "Authorization: Bearer $$GESTORIA_OWNER_TOKEN" \
		http://127.0.0.1:$${PORT:-8787}/api/security/digest | $(VENV)/bin/python -m json.tool
