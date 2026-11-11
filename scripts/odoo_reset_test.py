"""Explicitly destroy this synthetic compose project only. Never called by tests implicitly."""
import argparse
from odoo_bootstrap import state_dir,compose
p=argparse.ArgumentParser();p.add_argument('--state-dir',required=True);p.add_argument('--confirm-destroy-synthetic-lab',action='store_true',required=True);args=p.parse_args()
state=state_dir(args.state_dir)
compose(state,'--profile','app','down','--volumes')
print('Named synthetic lab containers and volumes removed. Private host credentials/backups retained for deliberate cleanup.')
