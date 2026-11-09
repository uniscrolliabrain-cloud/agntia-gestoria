# Decisiones C02

- Fijar commits y referencias de imagen por separado. Registrar equivalencia no verificada en lugar de equiparar un paquete nightly con HEAD del upstream.
- Verificación estática mediante AST/XML/CSV y SHA-256, sin importar upstream ni copiarlo en el producto. Los checks capturan contratos que afectarán al aislamiento y mapeo; no activan capacidades.
- Corregir la ruta de manifiesto citada: `addons/l10n_es/__manifest__.py`.
- Descubrir `company_ids` y reglas compartidas en lugar de trasladar ejemplos de Odoo antiguo. La política de binding futuro deberá ser más restrictiva que los permisos generales del ERP.
- Preservar todas las fórmulas y archivos originales de C01. Ningún cambio en agente, producción, configuración real o secretos.
- Entregar PR borrador mientras falten contratos reales. No avanzar por los gates como si hubiera una instalación probada.
