import test from "node:test";
import assert from "node:assert/strict";

import {
  gestoriaTools,
  humanOnly,
  isHumanOnly,
  proposalTools,
  readOnlyTools,
} from "../src/index.ts";

const client = {};

test("C04: ninguna herramienta de lectura muta estado", () => {
  const tools = readOnlyTools(client);
  assert.ok(tools.length > 0);
  for (const tool of tools) assert.equal(tool.mutates, false, tool.name);
});

test("C04: las propuestas se declaran como mutación", () => {
  const tools = proposalTools(client);
  assert.ok(tools.length > 0);
  for (const tool of tools) assert.equal(tool.mutates, true, tool.name);
});

test("C04: los catálogos no se solapan en nombres", () => {
  const read = new Set(readOnlyTools(client).map((tool) => tool.name));
  for (const tool of proposalTools(client)) assert.ok(!read.has(tool.name), tool.name);
  for (const tool of readOnlyTools(client)) {
    assert.ok(!tool.name.startsWith("rrhh.closure.approve"));
    assert.ok(!tool.name.startsWith("rrhh.closure.export"));
  }
});

test("C04: el catálogo completo es la unión de ambos", () => {
  const names = gestoriaTools(client).map((tool) => tool.name);
  assert.equal(new Set(names).size, names.length);
  assert.equal(names.length, readOnlyTools(client).length + proposalTools(client).length);
  assert.ok(names.includes("rrhh.closure.prepare"));
  assert.ok(names.includes("rrhh.closure.read"));
});

test("C04: el cierre preparado no se ofrece como lectura", () => {
  assert.ok(!readOnlyTools(client).some((tool) => tool.name === "rrhh.closure.prepare"));
  assert.ok(proposalTools(client).some((tool) => tool.name === "rrhh.closure.prepare"));
});

test("C04: las operaciones humanas no están en ningún catálogo del agente", () => {
  const names = new Set(gestoriaTools(client).map((tool) => tool.name));
  for (const name of humanOnly) {
    assert.ok(isHumanOnly(name));
    assert.ok(!names.has(name), name);
  }
  assert.equal(isHumanOnly("rrhh.closure.prepare"), false);
});

test("C04: toda herramienta tiene nombre y descripción utilizables", () => {
  for (const tool of gestoriaTools(client)) {
    assert.match(tool.name, /^[a-z][a-z0-9]*(\.[a-z0-9]+)+$/);
    assert.ok(tool.description.length > 10, tool.name);
  }
});
