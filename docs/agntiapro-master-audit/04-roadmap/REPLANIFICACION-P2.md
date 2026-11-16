# Ajuste del roadmap tras inspección de código

**Gate previo inmediato:** GES-P2-01 y GES-P2-02 pasan a C04/C05 antes de cualquier integración de RRHH con Agente. C03 introduce autenticación de delegación sin romper sesiones legacy. C06–C10 verifican Odoo real y su ledger, sin reescribir bridge. C18 agrega feed durable solo después de verificar transacciones existentes. C21 consume approvals canónicas sin permitir a agentes aprobar.

**Secuencia de implementación segura:** C00/C01 → C02 → C03 → C04 → C05 → C06/C07 → C08/C09/C10 → C11/C12 → C13/C14/C15 → C16 → C17 (dependencia regulada) → C18/C19 → C20/C21 → C22/C23.

**Paralelización:** golden cases 303/130 pueden prepararse con C06/C07 en ramas distintas; no modificar `tax.py` simultáneamente. UI de lectura puede empezar tras C05; escritura solo después de C21. Banca C17 puede quedar BLOCKED por proveedor sin detener C18/C19. Los reportes de cada campaña deben actualizar las posteriores, sin auto-merge.

**Gates:** 0 mutaciones catalogadas como lectura; 0 accesos cross-tenant; 0 commits Odoo duplicados; 0 tests obligatorios skipped; restauración real demostrada; versiones del padre e hijo fijadas.
