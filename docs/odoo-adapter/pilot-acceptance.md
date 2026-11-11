# Aceptación de piloto · no aprobada aún

El propietario pidió implementar todo el código y ejecutar Docker posteriormente con otra IA. Estado: pruebas locales disponibles; Odoo real y despliegue NO VERIFICADOS. No interpretar código presente como gate real aprobado.

- [ ] Construir la imagen exacta; registrar digest final y SHA efectivo.
- [ ] Instalar dos DB desde cero con account/l10n_es/bridge, comprobar versión, ACL y grupos mínimos.
- [ ] Ejecutar variante sin account y sin permisos: capacidades unsupported, sin fallback admin.
- [ ] Ejecutar smoke y suite live A–E; guardar conteos, logs sanitizados y tiempos reales.
- [ ] Ampliar D a revisión/cálculo completo tras cambio real; comprobar informes stale en UI.
- [ ] Probar carrera concurrente de dos escrituras firmadas iguales y unicidad del ledger/borrador, rollback de fallo durante create, crash/recovery y expiración de lease.
- [ ] Rotación/revocación de API key/HMAC; conexión DB equivocada; fallo Odoo/SQLite; no secretos en logs, reportes o eventos.
- [ ] Backup/restore real de PostgreSQL+filestore y SQLite+originales cifrados con claves recuperables.
- [ ] Browser desktop/móvil y Hono autenticado con credenciales acotadas; no proxy ORM libre.
- [ ] Verificar 303/130 originales y cero importados reviewed; casos fuera de ámbito bloqueados.
- [ ] Validar scanner de producción, RGPD/retención, cifrado en reposo, firewall/TLS y presupuesto operativo.
- [ ] Aceptación expresa del propietario antes de producción o wiring en agente.

Pruebas unitarias con mocks no sustituyen ninguna casilla. Registrar FAIL/BLOCKED con causa; no alterar tests para ocultar defectos. Hasta completar estas condiciones mantener escrituras de producción desactivadas y usar solo fixtures.
