import test from "node:test";
import assert from "node:assert/strict";

import { GestoriaError, createGestoriaClient, parseFailure } from "../src/index.ts";

const TOKEN = "token-de-prueba-que-no-debe-filtrarse";

const responder = (status, body, { json = true } = {}) => async (url, init) => {
  const text = json ? JSON.stringify(body) : String(body);
  return new Response(text, {
    status,
    headers: { "Content-Type": json ? "application/json" : "text/html" },
  });
};

const clientWith = (fetchImpl) =>
  createGestoriaClient({ baseUrl: "http://127.0.0.1:9", token: TOKEN, fetchImpl });

async function failure(status, body, options) {
  const client = clientWith(responder(status, body, options));
  try {
    await client.health("empresa-de-prueba");
  } catch (error) {
    return error;
  }
  assert.fail("la llamada debía fallar");
}

test("C05: el error de integración conserva su código", async () => {
  const error = await failure(409, { code: "stale_capabilities", message: "Capacidades caducadas", correlation_id: "c", retryable: false });
  assert.ok(error instanceof GestoriaError);
  assert.equal(error.status, 409);
  assert.equal(error.code, "stale_capabilities");
  assert.equal(error.message, "Capacidades caducadas");
});

test("C05: el error anidado en detail también se interpreta", async () => {
  const error = await failure(403, { detail: { code: "forbidden", message: "Operación no autorizada" } });
  assert.equal(error.code, "forbidden");
  assert.equal(error.message, "Operación no autorizada");
});

test("C05: detail como texto produce el código del estado", async () => {
  const error = await failure(404, { detail: "Recurso no encontrado" });
  assert.equal(error.code, "not_found");
  assert.equal(error.message, "Recurso no encontrado");
});

test("C05: la validación de FastAPI se normaliza a validation", async () => {
  const error = await failure(422, { detail: [{ loc: ["body"], msg: "field required", type: "missing" }] });
  assert.equal(error.code, "validation");
  assert.equal(error.message, "field required");
});

test("C05: una respuesta no JSON no filtra el cuerpo crudo", async () => {
  const error = await failure(503, "<html><body>stack interno</body></html>", { json: false });
  assert.equal(error.code, "provider_unavailable");
  assert.ok(!error.message.includes("stack interno"));
  assert.ok(!error.message.includes("<html"));
});

test("C05: un cuerpo vacío en 401 se traduce a auth", async () => {
  const client = clientWith(async () => new Response("", { status: 401 }));
  await assert.rejects(
    () => client.health("empresa-de-prueba"),
    (error) => error instanceof GestoriaError && error.code === "auth",
  );
});

test("C05: un cuerpo sin código ni detail cae en el código de estado", async () => {
  const error = await failure(409, { message: "conflicto sin código" });
  assert.equal(error.code, "conflict");
});

test("C05: la credencial nunca aparece en el error", async () => {
  const error = await failure(403, { code: "forbidden", message: "Operación no autorizada" });
  assert.ok(!error.message.includes(TOKEN));
  assert.ok(!String(error.stack ?? "").includes(TOKEN));
});

test("C05: la petición envía la cabecera Authorization", async () => {
  let seen = null;
  const client = clientWith(async (url, init) => {
    seen = new Headers(init.headers);
    return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { "Content-Type": "application/json" } });
  });
  const result = await client.health("empresa-de-prueba");
  assert.deepEqual(result, { ok: true });
  assert.equal(seen.get("Authorization"), `Bearer ${TOKEN}`);
});

test("C05: parseFailure acepta cualquier forma sin lanzar", () => {
  assert.deepEqual(parseFailure(400, null), { code: "http_error", message: "HTTP 400" });
  assert.deepEqual(parseFailure(409, "texto"), { code: "conflict", message: "HTTP 409" });
  assert.deepEqual(parseFailure(422, { detail: [] }), { code: "validation", message: "Entrada inválida" });
  assert.equal(parseFailure(503, { code: "provider_unavailable" }).message, "HTTP 503");
});
