import { Hono } from 'hono';
import type { Context } from 'hono';
import type { Gestoria } from './index.js';
export declare function gestoriaRoutes(forActor: (context: Context) => Promise<Gestoria>): Hono;
