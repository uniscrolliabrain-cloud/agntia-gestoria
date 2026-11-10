"""Run inside an Odoo shell with the synthetic database bound to env."""

from datetime import timedelta
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from odoo import Command, fields


def query_partner(database, key, partner_id):
    request = Request(
        "http://127.0.0.1:8069/json/2/res.partner/search_read",
        data=json.dumps({"domain": [["id", "=", partner_id]], "fields": ["name"]}).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Odoo-Database": database,
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.load(response)


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
        if query_partner(database, key, partner.id) != [{"id": partner.id, "name": name}]:
            raise RuntimeError(f"{database}: JSON-2 returned an unexpected partner")
        try:
            query_partner(other_database, key, partner.id)
        except HTTPError as error:
            if error.code not in (401, 403):
                raise
        else:
            raise RuntimeError(f"{other_database}: accepted the other database's API key")
        print(f"{database}: contacts JSON-2 PASS; cross-database key rejected")
    finally:
        bot.unlink()
        partner.unlink()
        env.cr.commit()


run_smoke(env)
