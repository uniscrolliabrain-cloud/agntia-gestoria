import hashlib
import os
from pathlib import Path
from cryptography.fernet import Fernet,InvalidToken
from ..errors import reject


def cipher():
    ref=os.getenv('ODOO_DOCUMENT_KEY_ENV','ODOO_DOCUMENT_KEY')
    try:return Fernet(os.environ[ref].encode())
    except (ValueError,KeyError):reject('not_configured','Clave de cifrado documental no configurada',424)


def store_blob(path,data):
    encrypted=cipher().encrypt(data)
    with Path(path).open('xb') as handle:handle.write(encrypted)


def read_blob(path,expected_hash):
    try:data=cipher().decrypt(Path(path).read_bytes())
    except (InvalidToken,OSError):reject('integrity','Documento cifrado no recuperable',503)
    if hashlib.sha256(data).hexdigest()!=expected_hash:reject('integrity','Checksum documental incorrecto',503)
    return data
