# ADR 0002 · Cierre de expedientes reservado a revisión humana

Estado: propuesta para revisión sobre la [PR #4](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/4). Conserva el [ADR 0001](0001-batch-implementation.md) y el inventario original. Se incorpora a la rama del adaptador la corrección preparada en la [PR #6](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/6), como parte del refuerzo previo a la integración solicitado por el propietario.

La API reserva el cierre a `owner` y `reviewer` y sigue exigiendo una revisión vigente. La UI muestra la acción a esos roles. El catálogo del SDK de agentes deja de exponer el cierre. La regresión prueba el rechazo de un agente incluso cuando la revisión existe y la finalización por el propietario.

La política de fuentes registra el nuevo hash exacto de `app.py` y los cinco archivos adicionales de esta corrección. El inventario original, las fórmulas, las fuentes y el almacenamiento conservan sus hashes. La modificación de la política es parte de esta propuesta revisable.
