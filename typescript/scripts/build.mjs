import { stripTypeScriptTypes } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
await mkdir(new URL('../dist/', import.meta.url), {recursive:true});
for (const file of ['index','agents','hono','odoo','odoo-agent-tools','odoo-routes']) {
  const source=await readFile(new URL(`../${file}.ts`,import.meta.url),'utf8');
  const output=stripTypeScriptTypes(source,{mode:'strip'}).replaceAll("'./index.ts'","'./index.js'").replaceAll("'./odoo.ts'","'./odoo.js'").replaceAll("'./odoo-routes.ts'","'./odoo-routes.js'");
  await writeFile(new URL(`../dist/${file}.js`,import.meta.url),output);
}
