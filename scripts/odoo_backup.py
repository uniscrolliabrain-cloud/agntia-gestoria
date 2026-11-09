"""Synthetic Odoo DB+filestore backup/restore. Stops only this lab; never customer data."""
import argparse
from datetime import datetime,timezone
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
from odoo_bootstrap import ROOT,state_dir,compose


def binary(state,args,data=None):
    if os.getenv('DOCKER_HOST'):raise SystemExit('Remote Docker selector refused')
    env={**os.environ,'AGNTIA_LAB_STATE_DIR':str(state)}
    result=subprocess.run(['docker','compose','-p','agntia-gestoria-synthetic-lab','-f',str(ROOT/'infra/odoo/compose.yaml'),*args],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    if result.returncode:raise SystemExit('Private lab backup command failed; no raw output printed')
    return result.stdout


def main():
    p=argparse.ArgumentParser();p.add_argument('--state-dir',required=True);p.add_argument('--database',choices=['agntia_test_a','agntia_test_b'],required=True);p.add_argument('--backup',action='store_true');p.add_argument('--restore-from');p.add_argument('--confirm-synthetic-restore',action='store_true');args=p.parse_args()
    if bool(args.backup)==bool(args.restore_from):p.error('Choose backup or restore')
    state=state_dir(args.state_dir);database=args.database
    if args.backup:
        folder=state/'backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');folder.mkdir(parents=True)
        previous=binary(state,['ps','--status','running','--services']).decode().splitlines()
        compose(state,'stop','worker','gestoria','odoo')
        try:
            dump=binary(state,['exec','-T','db','pg_dump','-U','odoo','-Fc',database]);(folder/'database.dump').write_bytes(dump)
            archive=binary(state,['run','--rm','--no-deps','--entrypoint','tar','odoo','-czf','-','-C','/var/lib/odoo','filestore/'+database]);(folder/'filestore.tar.gz').write_bytes(archive)
            manifest={'synthetic':True,'database':database,'db_sha256':hashlib.sha256(dump).hexdigest(),'filestore_sha256':hashlib.sha256(archive).hexdigest(),'source_sha':'60657b50d171ddf84ab58717fdee5ac26031065b'}
            (folder/'manifest.json').write_text(json.dumps(manifest,indent=2))
        finally:
            for name in ('odoo','gestoria','worker'):
                if name in previous:compose(state,'--profile','app','up','-d',name)
        print(json.dumps({'backup_directory':str(folder),'status':'backup_created_restore_not_yet_verified'}))
    else:
        if not args.confirm_synthetic_restore:p.error('Explicit test-only restore confirmation required')
        folder=Path(args.restore_from).resolve()
        if state/'backups' not in folder.parents:raise SystemExit('Restore source must be this lab private backup')
        manifest=json.loads((folder/'manifest.json').read_text());dump=(folder/'database.dump').read_bytes();archive=(folder/'filestore.tar.gz').read_bytes()
        if manifest.get('synthetic') is not True or manifest['database']!=database or hashlib.sha256(dump).hexdigest()!=manifest['db_sha256'] or hashlib.sha256(archive).hexdigest()!=manifest['filestore_sha256']:raise SystemExit('Backup identity/checksum mismatch')
        with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tar:
            for member in tar.getmembers():
                if member.name.startswith('/') or '..' in Path(member.name).parts or member.issym() or member.islnk() or not (member.name=='filestore/'+database or member.name.startswith('filestore/'+database+'/')):raise SystemExit('Unsafe filestore archive')
        target='agntia_test_restore'
        binary(state,['exec','-T','db','dropdb','--if-exists','-U','odoo',target])
        binary(state,['exec','-T','db','createdb','-U','odoo',target])
        binary(state,['exec','-T','db','pg_restore','-U','odoo','--no-owner','-d',target],dump)
        binary(state,['run','--rm','--no-deps','--entrypoint','tar','odoo','-xzf','-','-C','/var/lib/odoo','--transform=s|^filestore/'+database+'|filestore/'+target+'|'],archive)
        count=binary(state,['exec','-T','db','psql','-U','odoo','-d',target,'-Atc','SELECT count(*) FROM account_move']).decode().strip()
        if not count.isdigit() or int(count)<1:raise SystemExit('Restored invoice fixture missing')
        print(json.dumps({'status':'synthetic_restore_verified','target':target,'account_move_count':int(count),'checksums_verified':True}))


if __name__=='__main__':main()
