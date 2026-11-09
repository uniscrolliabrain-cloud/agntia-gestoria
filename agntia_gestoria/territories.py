"""Preparation coverage, separate from automatic tax assessment or legal routing."""
TERRITORIES = {
    'common': ('Península y Baleares (territorio común)', ['lgt', 'vat']),
    'canarias': ('Canarias', ['canarias-ref']),
    'araba': ('Álava / Araba', ['basque-concert']),
    'bizkaia': ('Bizkaia', ['basque-concert']),
    'gipuzkoa': ('Gipuzkoa', ['basque-concert']),
    'navarra': ('Navarra', ['navarra-agreement']),
    'ceuta': ('Ceuta', ['ipsi']),
    'melilla': ('Melilla', ['ipsi']),
}
LEGACY = {'common': ['common'], 'canarias': ['canarias'], 'foral': [], **{key: [key] for key in ('araba','bizkaia','gipuzkoa','navarra','ceuta','melilla')}}


def territorial_profile(company):
    selected = company.get('operation_territories', [])
    regions = list(dict.fromkeys(selected or LEGACY.get(company['tax_territory'], [])))
    assignments = company.get('tax_administrations', {})
    return {
        'declared_operation_territories': regions,
        'tax_administrations': assignments,
        'assignment_status': 'declared_requires_review',
        'legacy_foral_unspecified': company['tax_territory'] == 'foral' and not selected,
        'multiple_territories': len(regions) > 1,
        'automatic_tax_calculation': False,
        'notice': 'Operar en un territorio no determina por sí solo dónde tributar. Revisar por impuesto, ejercicio y puntos de conexión; no se asignan porcentajes de reparto automáticamente.',
    }
