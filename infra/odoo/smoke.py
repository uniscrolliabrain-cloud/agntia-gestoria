"""Run inside an Odoo shell with the synthetic database bound to env."""

from datetime import timedelta
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from odoo import Command, fields


def search_read(database, key, model, domain, field_names, context=None):
    request = Request(
        f"http://127.0.0.1:8069/json/2/{model}/search_read",
        data=json.dumps({"domain": domain, "fields": field_names, "limit": 1, "context": context or {}}).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Odoo-Database": database,
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def require_rejection(database, key, model, domain, field_names, *, statuses, context=None):
    try:
        search_read(database, key, model, domain, field_names, context)
    except HTTPError as error:
        if error.code in statuses:
            return
        raise
    raise RuntimeError(f"{database}: expected {model} to reject the request")


def create_bot(env, name, company, groups):
    bot = env["res.users"].with_context(no_reset_password=True).create({
        "name": name,
        "login": name,
        "company_id": company.id,
        "company_ids": [Command.set(company.ids)],
        "group_ids": [Command.set([env.ref(group).id for group in groups])],
    })
    if bot.has_group("base.group_system"):
        raise RuntimeError("Synthetic bot unexpectedly has system permissions")
    key = env["res.users.apikeys"].with_user(bot)._generate(
        "rpc", "C03 smoke", fields.Datetime.now() + timedelta(minutes=15),
    )
    return bot, key


def run_smoke(env):
    database = env.cr.dbname
    other_database = {"agntia_test_a": "agntia_test_b", "agntia_test_b": "agntia_test_a"}[database]
    name = f"C03 synthetic {uuid4().hex}"
    company = env.ref("base.main_company")
    companies = env["res.company"]
    peer_name = "C03 synthetic peer company"
    peer = companies.search([("name", "=", peer_name)], limit=1) or companies.create({"name": peer_name})
    partner, foreign, shared = env["res.partner"].create([
        {"name": name, "company_id": company.id},
        {"name": f"{name} peer", "company_id": peer.id},
        {"name": f"{name} shared", "company_id": False},
    ])
    bot, key = create_bot(env, name, company, ["base.group_user"])
    accounting = "account.move" in env
    if accounting:
        reader, reader_key = create_bot(env, f"{name} accounts", company, ["base.group_user", "account.group_account_readonly"])
        journal = env["account.journal"].create({
            "name": name, "code": uuid4().hex[:5].upper(), "type": "sale", "company_id": company.id,
        })
        invoice = env["account.move"].with_company(company).create({
            "move_type": "out_invoice", "partner_id": partner.id, "journal_id": journal.id,
        })
    env.cr.commit()
    try:
        partner_filter = [["id", "=", partner.id]]
        if search_read(database, key, "res.partner", partner_filter, ["name"]) != [{"id": partner.id, "name": name}]:
            raise RuntimeError(f"{database}: JSON-2 returned an unexpected partner")
        require_rejection(other_database, key, "res.partner", partner_filter, ["name"], statuses=(401, 403))
        require_rejection(database, key, "ir.config_parameter", [], ["key"], statuses=(403,))
        foreign_filter = [["id", "=", foreign.id]]
        if search_read(database, key, "res.partner", foreign_filter, ["name"]):
            raise RuntimeError(f"{database}: bot read a contact belonging to the peer company")
        require_rejection(
            database, key, "res.partner", foreign_filter, ["name"],
            statuses=(403,), context={"allowed_company_ids": peer.ids},
        )
        if search_read(database, key, "res.partner", [["id", "=", shared.id]], ["name"]) != [{"id": shared.id, "name": shared.name}]:
            raise RuntimeError(f"{database}: expected native Odoo to return the shared contact")
        print(f"{database}: own and shared contacts visible; peer company contact and forced context rejected")
        if accounting:
            invoice_filter = [["id", "=", invoice.id]]
            require_rejection(database, key, "account.move", invoice_filter, ["state"], statuses=(403,))
            expected = [{"id": invoice.id, "state": "draft", "move_type": "out_invoice"}]
            if search_read(database, reader_key, "account.move", invoice_filter, ["state", "move_type"]) != expected:
                raise RuntimeError(f"{database}: accounting reader did not receive the expected draft")
            print(f"{database}: read-only accounting user read draft; standard internal user denied")
        else:
            require_rejection(database, key, "account.move", [], ["state"], statuses=(404,))
            print(f"{database}: account.move unavailable without account")
    finally:
        if accounting:
            invoice.unlink()
            journal.unlink()
            reader.unlink()
        bot.unlink()
        (partner | foreign | shared).unlink()
        env.cr.commit()


run_smoke(env)
