"""Run after installing the package and Playwright Chromium: python scripts/browser_check.py.
Uses an isolated database and generated demonstration records, never production data.
"""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

from playwright.sync_api import sync_playwright

with tempfile.TemporaryDirectory() as directory:
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    env={**os.environ,'GESTORIA_DATA_DIR':directory,'GESTORIA_OWNER_TOKEN':'','GESTORIA_ACTORS_JSON':'{}','GESTORIA_ALLOW_LOCAL_OWNER':'true'}
    server=subprocess.Popen([sys.executable,'-m','agntia_gestoria.cli','--port',str(port)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    root=f'http://127.0.0.1:{port}'
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(root+'/api/status',timeout=.5):break
            except OSError:time.sleep(.1)
        def post(path,data):
            request=urllib.request.Request(root+path,json.dumps(data).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(request) as response:return json.load(response)
        company=post('/api/companies',{'name':'Empresa de demostración','legal_form':'autonomo','tax_territory':'common'})
        path='/api/companies/'+company['id']
        for month in range(1,7):
            for kind,amount in [('income',1000+month*200),('expense',500+month*30)]:
                post(path+'/tax-records',{'external_id':f'{month}-{kind}','operation_date':f'2026-{month:02}-10','kind':kind,'description':'Demostración','tax_kind':'iva','base_amount':str(amount),'tax_amount':str(round(amount*.21,2)),'category':'ordinary'})
        with sync_playwright() as p:
            browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1100})
            failures=[];page.on('pageerror',lambda error:failures.append(str(error)))
            page.goto(root);page.get_by_text('El pulso de tu negocio',exact=True).wait_for()
            page.locator('.kpi').first.wait_for();assert page.locator('.kpi').count()==4
            page.locator('.chart-card rect').first.focus();assert 'Ingresos' in page.locator('.chart-detail').inner_text()
            Path('test-results').mkdir(exist_ok=True)
            page.screenshot(path='test-results/dashboard-desktop.png',full_page=True)
            page.get_by_role('button',name='Generar informe',exact=True).click()
            page.get_by_role('link',name='Presentación PowerPoint').first.wait_for()
            with page.expect_download() as download:page.get_by_role('link',name='Presentación PowerPoint').first.click()
            assert download.value.suggested_filename.endswith('.pptx')
            page.locator('[data-tab="tax"]').click();page.get_by_role('button',name='Añadir registro',exact=True).click()
            page.locator('input[name="external_id"]').fill('manual-record');page.locator('input[name="description"]').fill('Ingreso manual')
            page.locator('input[name="base_amount"]').fill('100');page.locator('input[name="tax_amount"]').fill('21')
            page.get_by_role('button',name='Guardar',exact=True).click();page.get_by_role('heading',name='Ingreso manual',exact=True).wait_for()
            page.locator('[data-tab="dashboard"]').click();page.locator('.kpi').first.wait_for()
            page.set_viewport_size({'width':390,'height':844});page.screenshot(path='test-results/dashboard-mobile.png',full_page=True)
            overflow=page.evaluate('''() => [...document.querySelectorAll('body *')].filter(e => { const r=e.getBoundingClientRect(); return r.width && (r.right>innerWidth+1 || r.left< -1) && getComputedStyle(e).position !== 'fixed'; }).map(e=>({tag:e.tagName,cls:e.className,width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right})).slice(0,20)''')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal mobile overflow: '+json.dumps(overflow)
            assert not failures, failures
            browser.close()
        print('Desktop/mobile dashboard, report download and record creation passed')
    finally:
        server.terminate()
        try:server.wait(timeout=5)
        except subprocess.TimeoutExpired:server.kill();server.wait()
