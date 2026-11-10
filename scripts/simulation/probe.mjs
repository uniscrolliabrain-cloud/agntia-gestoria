import assert from "node:assert/strict";
import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Hono } from "hono";

const env = process.env;
const moduleUrl = name => pathToFileURL(path.join(env.GESTORIA_PROBE_CHECKOUT, "typescript", "dist", name));
// Reuse Hono installed in the scratch consumer when loading the packaged adapter.
const scratch = new URL("./adapter/", import.meta.url);
await mkdir(scratch, { recursive: true });
for (const filename of (await readdir(moduleUrl(""))).filter(name => name.endsWith(".js"))) {
  await writeFile(new URL(filename, scratch), await readFile(moduleUrl(filename)));
}
await writeFile(new URL("package.json", scratch), JSON.stringify({ type: "module" }));
const { Gestoria } = await import(new URL("index.js", scratch));
const { agentTools } = await import(new URL("agents.js", scratch));
const { gestoriaRoutes } = await import(new URL("hono.js", scratch));
const agent = new Gestoria(env.GESTORIA_PROBE_URL, env.GESTORIA_PROBE_AGENT);
const owner = new Gestoria(env.GESTORIA_PROBE_URL, env.GESTORIA_PROBE_OWNER);
const a = env.GESTORIA_PROBE_A;
const b = env.GESTORIA_PROBE_B;
const app = new Hono();
app.use("/api/*", async (ctx, next) => {
  if (ctx.req.header("X-Synthetic-Actor") !== "agent-a") return ctx.json({ error: "Unauthorized" }, 401);
  await next();
});
app.route("/api", gestoriaRoutes(async () => agent));
const headers = { "X-Synthetic-Actor": "agent-a", "Content-Type": "application/json" };
const request = (route, payload) => app.request(route, {
  method: payload === undefined ? "GET" : "POST",
  headers,
  body: payload === undefined ? undefined : JSON.stringify(payload),
});
assert.equal((await app.request("/api/companies")).status, 401);
assert.equal((await request("/api/companies")).status, 200);
assert.equal((await request(`/api/companies/${b}/cases`)).status, 404);
const root = `/api/companies/${a}`;
const tools = agentTools(agent, a);
const record = {
  external_id: "sdk-probe-1", operation_date: "2026-03-31", kind: "income",
  description: "Venta sintética", tax_kind: "none", base_amount: "100.10", tax_amount: "0",
};
await tools.create_tax_record.execute(record);
assert.equal((await request(`${root}/tax-records`, record)).status, 409);
assert.equal((await tools.list_tax_records.execute()).length, 1);
const draft = await tools.create_case.execute({ title: "Expediente sintético" });
const casePath = `${root}/cases/${draft.id}`;
await tools.submit_review.execute({ caseId: draft.id, revision: 0 });
const review = { revision: 1, decision: "approve", notes: "Aprobación sintética de prueba", verified_source_ids: [] };
assert.equal((await request(`${casePath}/review`, review)).status, 403);
await owner.request(`${casePath}/review`, review);
const fixed = env.GESTORIA_PROBE_VARIANT === "fixed";
assert.equal("close_reviewed_case" in tools, !fixed);
assert.equal((await request(`${casePath}/close`, { revision: 2 })).status, fixed ? 403 : 200);
if (fixed) assert.equal((await owner.request(`${casePath}/close`, { revision: 2 })).outcome, "internal_complete");
console.log(`${env.GESTORIA_PROBE_VARIANT}: SDK + Hono + FastAPI synthetic checks PASS (agent close ${fixed ? "denied" : "reproduced"})`);
if (env.GESTORIA_PROBE_AGENTE) {
  const { simulate } = await import("./runtime-probe.mts");
  await simulate(env.GESTORIA_PROBE_AGENTE, tools, draft.id);
}
