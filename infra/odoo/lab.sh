#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
compose=(docker compose -p agntia-odoo-lab -f compose.yaml)

sql() {
    local database=$1
    shift
    "${compose[@]}" exec -T db psql -XAt -v ON_ERROR_STOP=1 -U postgres -d "$database" "$@"
}

require_module() {
    local state
    state=$(sql "$1" -c "SELECT state FROM ir_module_module WHERE name = '$2'")
    if [[ $state != installed ]]; then
        printf '%s: módulo %s esperado installed; observado %s\n' "$1" "$2" "${state:-ausente}" >&2
        return 1
    fi
    sql "$1" -c "SELECT name, state, latest_version FROM ir_module_module WHERE name = '$2'"
}

bootstrap() {
    local database=$1 modules=$2 table
    table=$(sql "$database" -c "SELECT to_regclass('public.ir_module_module')")
    if [[ -z $table ]]; then
        "${compose[@]}" run --rm --no-deps odoo --stop-after-init --no-http \
            --without-demo=all --database="$database" --init="$modules"
    fi
}

verify() {
    require_module agntia_test_a base
    require_module agntia_test_a contacts
    require_module agntia_test_b base
    require_module agntia_test_b contacts
    require_module agntia_test_b account
    require_module agntia_test_b l10n_es
    if [[ $(sql agntia_test_a -c "SELECT count(*) FROM ir_module_module WHERE name = 'account' AND state = 'installed'") != 0 ]]; then
        printf 'agntia_test_a debe permanecer sin account\n' >&2
        return 1
    fi
    "${compose[@]}" exec -T odoo odoo --version
}

case "${1:-}" in
    up)
        "${compose[@]}" up -d --wait --wait-timeout 90 db
        bootstrap agntia_test_a base,contacts
        bootstrap agntia_test_b base,contacts,account,l10n_es
        "${compose[@]}" up -d --wait --wait-timeout 150 odoo
        verify
        ;;
    verify) verify ;;
    smoke)
        for database in agntia_test_a agntia_test_b; do
            "${compose[@]}" exec -T odoo bash -ec '
                exec odoo shell --no-http --database="$1" --db_host="$HOST" \
                    --db_user="$USER" --db_password="$PASSWORD"
            ' _ "$database" < smoke.py
        done
        ;;
    logs) "${compose[@]}" logs --no-color ;;
    stop) "${compose[@]}" down ;;
    *)
        printf 'Uso: bash lab.sh {up|verify|smoke|logs|stop}\n' >&2
        exit 2
        ;;
esac
