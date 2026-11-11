import { Hono } from 'hono';
import { allowedOdooRoute } from './odoo-routes.ts';
import type { Context } from 'hono';
import { Gestoria, GestoriaError } from './index.ts';
/** The host authenticates each request and supplies that actor's client, not a shared owner. */
export function gestoriaRoutes(forActor: (context: Context) => Promise<Gestoria>) {
  const router = new Hono();
  router.all('/*', async c => {
    const path = c.req.path;
    if (path.includes('/integrations/odoo') && !allowedOdooRoute(c.req.method,path)) return c.json({error:'Unsupported Odoo business capability'},404);
    // Mount at /api. Never expose login/logout or service credentials through this adapter.
    if (!/^\/api\/(companies(?:\/|$)|sources$|status$|tax-capabilities$)/.test(path)) return c.json({ error: 'Unsupported path' }, 404);
    if (!['GET', 'POST', 'PUT'].includes(c.req.method)) return c.json({ error: 'Unsupported method' }, 405);
    if (/\/(download(?:\/[^/]+)?|export|calendar\.ics)$/.test(path) || /\/documents$/.test(path) && c.req.method !== 'GET' || /\/preview-csv$/.test(path)) return c.json({ error: 'Use the service document/export endpoints directly with server-side authorization' }, 400);
    try {
      const client = await forActor(c);
      return c.json(await client.request(path + new URL(c.req.url).search, c.req.method === 'GET' ? undefined : await c.req.json(), c.req.method));
    } catch (error) {
      if (error instanceof GestoriaError) return new Response(JSON.stringify({ detail: error.detail }), { status: error.status, headers: { 'Content-Type': 'application/json' } });
      return c.json({ error: 'Request could not be completed' }, 400);
    }
  });
  return router;
}
