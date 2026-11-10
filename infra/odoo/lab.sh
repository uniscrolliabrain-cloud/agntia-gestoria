#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
compose=(docker compose -p agntia-odoo-lab -f compose.yaml)
# Git Bash must pass container paths to the native Docker CLI unchanged.
export MSYS_NO_PATHCONV=1

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

recovery() (
    local_source=agntia_test_b
    scratch=$(mktemp -d)
    target="agntia_test_restore_$(python3 -c 'import secrets; print(secrets.token_hex(8))')"
    created=false
    cleanup() {
        status=$?
        if [[ $created == true ]]; then
            "${compose[@]}" exec -T db dropdb -U postgres "$target" || status=1
        fi
        rm -f -- "$scratch/db.dump" "$scratch/files.tar"
        rmdir -- "$scratch"
        exit "$status"
    }
    trap cleanup EXIT

    "${compose[@]}" exec -T odoo bash -ec '
        exec odoo shell --no-http --database=agntia_test_b --db_host="$HOST" \
            --db_user="$USER" --db_password="$PASSWORD"
    ' <<'PY'
name = "agntia-c03-recovery-fixture"
attachments = env["ir.attachment"]
existing = attachments.search([("name", "=", name)], limit=1)
if not existing:
    attachments.create({"name": name, "raw": b"agntia-c03-synthetic-attachment\n"})
env.cr.commit()
PY

    # Only the dedicated lab uses this command. The fixture DB is quiescent.
    "${compose[@]}" stop odoo
    "${compose[@]}" exec -T db pg_dump -U postgres -Fc "$local_source" > "$scratch/db.dump"
    "${compose[@]}" run --rm -T --no-deps --entrypoint tar odoo \
        -C "/var/lib/odoo/filestore/$local_source" -cf - . > "$scratch/files.tar"
    (cd "$scratch" && sha256sum db.dump files.tar)
    "${compose[@]}" exec -T db createdb -U postgres -O agntia_lab "$target"
    created=true
    "${compose[@]}" exec -T db pg_restore --exit-on-error --single-transaction \
        --no-owner --no-privileges --role=agntia_lab -U postgres -d "$target" < "$scratch/db.dump"
    require_module "$target" account
    require_module "$target" l10n_es

    # The temporary data dir belongs to this one-off container only.
    "${compose[@]}" run --rm -T --no-deps --entrypoint bash odoo -ec '
        scratch=$(mktemp -d)
        store="$scratch/filestore/$1"
        mkdir -p "$store"
        tar -xf - -C "$store"
        odoo shell --no-http --database="$1" --data-dir="$scratch" --db_host="$HOST" \
            --db_user="$USER" --db_password="$PASSWORD" <<PY
attachment = env["ir.attachment"].search([("name", "=", "agntia-c03-recovery-fixture")])
if len(attachment) != 1 or not attachment.store_fname:
    raise RuntimeError("Restored filestore fixture missing or ambiguous")
if attachment.raw != b"agntia-c03-synthetic-attachment\n":
    raise RuntimeError("Restored ORM attachment bytes differ from fixture")
print("Restored attachment verified through Odoo ORM")
PY
    ' _ "$target" < "$scratch/files.tar"
    "${compose[@]}" up -d --wait --wait-timeout 150 odoo
    printf 'Restored database and filestore attachment verified\n'
)

case "${1:-}" in
    up)
        "${compose[@]}" up -d --wait --wait-timeout 90 db
        bootstrap agntia_test_a base,contacts
        bootstrap agntia_test_b base,contacts,account,l10n_es
        "${compose[@]}" up -d --wait --wait-timeout 150 odoo
        verify
        ;;
    verify) verify ;;
    provenance)
        "${compose[@]}" exec -T odoo python3 -c "$(cat provenance.py)" < upstream-lock.json
        ;;
    smoke)
        for database in agntia_test_a agntia_test_b; do
            "${compose[@]}" exec -T odoo bash -ec '
                exec odoo shell --no-http --database="$1" --db_host="$HOST" \
                    --db_user="$USER" --db_password="$PASSWORD"
            ' _ "$database" < smoke.py
        done
        ;;
    recovery) recovery ;;
    logs) "${compose[@]}" logs --no-color ;;
    stop) "${compose[@]}" down ;;
    *)
        printf 'Uso: bash lab.sh {up|verify|provenance|smoke|recovery|logs|stop}\n' >&2
        exit 2
        ;;
esac
