"""CLI de operación: estado del rastro de auditoría de una empresa.

    python -m agntia_gestoria.integrations.security --db .agente --company <hex32>

Solo lee. No arranca el servicio ni envía nada a ningún sitio.
"""
import argparse
import json
import sys

from ...storage import Database, identifier
from ..rrhh.audit import trail


def main(argv=None):
    parser = argparse.ArgumentParser(prog='agntia-gestoria-security',
                                     description='Estado del rastro de auditoría (solo lectura)')
    parser.add_argument('--db', required=True, help='Directorio de datos del servicio')
    parser.add_argument('--company', required=True, help='Identificador hex32 de la empresa')
    args = parser.parse_args(argv)
    try:
        cid = identifier(args.company)
    except ValueError:
        print('Identificador de empresa inválido: se esperan 32 caracteres hexadecimales',
              file=sys.stderr)
        return 2
    database = Database(args.db)
    with database.connection() as connection:
        report = trail(connection, cid)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
