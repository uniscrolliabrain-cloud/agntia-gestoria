"""Run inside an Odoo shell with the synthetic database bound to env."""

from datetime import timedelta
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from odoo import Command, fields


def search_read(database, key, model, domain, field_names):
    request = Request(
        f"http://127.0.0.1:8069/json/2/{model}/search_read",
        data=json.dumps({"domain": domain, "fields": field_names, "limit": 1}).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Odoo-Database": database,
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def require_rejection(database, key, model, domain, field_names):
    try:
        search_read(database, key, model, domain, field_names)
    except HTTPError as error:
        if error.code in (401, 403):
            return
        raise
    raise RuntimeError(f"{database}: expected {model} to reject the request")


def run_smoke(env):
    database = env.cr.dbname
    other_database = {"agntia_test_a": "agntia_test_b", "agntia_test_b": "agntia_test_a"}[database]
    name = f"C03 synthetic {uuid4().hex}"
    company = env.ref("base.main_company")
    partner = env["res.partner"].create({"name": name, "company_id": company.id})
    bot = env["res.users"].with_context(no_reset_password=True).create({
        "name": name,
        "login": name,
        "company_id": company.id,
        "company_ids": [Command.set(company.ids)],
        "group_ids": [Command.set(env.ref("base.group_user").ids)],
    })
    if bot.has_group("base.group_system"):
        raise RuntimeError("Synthetic bot unexpectedly has system permissions")
    key = env["res.users.apikeys"].with_user(bot)._generate(
        "rpc", "C03 smoke", fields.Datetime.now() + timedelta(minutes=15),
    )
    env.cr.commit()
    try:
        partner_filter = [["id", "=", partner.id]]
        if search_read(database, key, "res.partner", partner_filter, ["name"]) != [{"id": partner.id, "name": name}]:
            raise RuntimeError(f"{database}: JSON-2 returned an unexpected partner")
        require_rejection(other_database, key, "res.partner", partner_filter, ["name"])
        require_rejection(database, key, "ir.config_parameter", [], ["key"])
        print(f"{database}: contacts JSON-2 PASS; cross-database and admin-model requests rejected")
    finally:
        bot.unlink()
        partner.unlink()
        env.cr.commit()


run_smoke(env)
