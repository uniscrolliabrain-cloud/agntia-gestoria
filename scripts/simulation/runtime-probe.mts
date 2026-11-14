import assert from "node:assert/strict";
import path from "node:path";
import { pathToFileURL } from "node:url";

export async function simulate(
  checkout: string, tools: { list_cases: { execute: () => Promise<unknown> } }, caseId: string,
) {
  const source = (relative: string) => pathToFileURL(path.join(checkout, "apps/server/src/engine", relative)).href;
  const { AgentRuntimeManager } = await import(source("agents/runtime.ts"));
  const { CapabilityRunner } = await import(source("execution/capability-runner.ts"));
  const { Executor } = await import(source("execution/executor.ts"));
  const manager = new AgentRuntimeManager();
  const runtime = await manager.spawn({ tenantId: "tenant-a", owner: "owner-a", roleId: "gestoria-reader" });
  const other = await manager.spawn({ tenantId: "tenant-b", owner: "owner-b", roleId: "gestoria-reader" });
  const context = (execution: typeof runtime) => ({
    ...execution, role: "agent", actorId: "synthetic-agent", requestId: execution.correlationId,
  });
  const capability = "gestoria.cases.read";
  const registry = {
    get: async (name: string) => name === capability
      ? { id: name, requiresApproval: false, idempotency: "idempotent", sideEffects: [] }
      : null,
  };
  let calls = 0;
  const executors = new Map([[capability, {
    run: async (ctx: { runtimeId: string }, _cap: string, inputs: Record<string, unknown>) => {
      assert.equal(ctx.runtimeId, runtime.runtimeId);
      if (Object.keys(inputs).length) throw new Error("unexpected tool inputs");
      calls++;
      const cases = await tools.list_cases.execute() as Array<{ id: string }>;
      assert.ok(cases.some(entry => entry.id === caseId));
      return cases;
    },
  }]]);
  const governance = {
    canExecuteTool: async (actor: { tenantId: string; runtimeId: string }) => ({
      allowed: actor.tenantId === runtime.tenantId && actor.runtimeId === runtime.runtimeId,
    }),
    canExecuteAction: async () => ({ allowed: false }),
  };
  const runner = new CapabilityRunner(registry, executors, governance, async () => ({ name: "Synthetic reader" }));
  const step = (id: string, capabilityId: string, inputs = {}) => ({
    id, title: id, capabilityId, inputs, dependsOn: [], status: "pending",
  });
  const read = step("read", capability);
  assert.equal((await new Executor(runner).execute(context(runtime), { steps: [read] })).status, "succeeded");
  await assert.rejects(runner.run(context(other), read), /authz denied/);
  await assert.rejects(runner.run(context(runtime), step("close", "gestoria.case.close")), /not found/);
  await assert.rejects(runner.run(context(runtime), step("read", capability, { companyId: "other" })), /unexpected/);
  assert.equal(calls, 1);
  console.log("Agente runtime + CapabilityRunner + SDK + FastAPI: tenant-scoped read PASS");

  // Disposable effect counter models a commit whose acknowledgement never arrived.
  const rows = new Map<string, Record<string, unknown>>();
  const key = (tenant: string, kind: string, id: string) => JSON.stringify([tenant, kind, id]);
  const db = {
    get: async (tenant: string, kind: string, id: string) => rows.get(key(tenant, kind, id)) ?? null,
    put: async (tenant: string, kind: string, row: { id: string }) => rows.set(key(tenant, kind, row.id), row),
    insertIfAbsent: async (tenant: string, kind: string, row: { id: string }) => {
      const id = key(tenant, kind, row.id);
      if (rows.has(id)) return false;
      rows.set(id, row);
      return true;
    },
  };
  const effect = "synthetic.external.effect";
  let committed = 0;
  const writeRunner = new CapabilityRunner(
    { get: async () => ({ id: effect, requiresApproval: false, idempotency: "non_idempotent", sideEffects: [{ kind: "external_write" }] }) },
    new Map([[effect, { run: async () => { committed++; throw new Error("synthetic acknowledgement lost after commit"); } }]]),
    undefined, undefined, db,
  );
  const write = step("write", effect);
  await assert.rejects(writeRunner.run(context(runtime), write), /acknowledgement lost/);
  await assert.rejects(writeRunner.run(context(runtime), write), /acknowledgement lost/);
  assert.equal(committed, 2);
  console.log("Diagnostic: existing Agente runner retried a failed claim after a simulated commit with lost acknowledgement");
  await manager.complete(runtime.runtimeId, 1);
  await manager.complete(other.runtimeId, 1);
  assert.equal(manager.get(runtime.runtimeId), undefined);
}
