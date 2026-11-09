from ...errors import reject


def remote_id(value):
    if type(value)==int and value>0:return value
    if isinstance(value,list) and value and type(value[0])==int and value[0]>0:return value[0]
    return None


def partner(row,company):
    if remote_id(row.get('company_id'))!=company:reject('scope_violation','Registro remoto fuera de la compañía vinculada',502)
    if type(row.get('id'))!=int or row['id']<=0:reject('invalid_response','Identidad remota inválida',502)
    for field in ('name','vat','email'):
        if row.get(field) not in (None,False) and not isinstance(row.get(field),str):reject('invalid_response','Campo de contacto remoto inválido',502)
    if type(row.get('is_company'))!=bool:reject('invalid_response','Clase de contacto remota inválida',502)
    return {'name':str(row.get('name') or '')[:160],'vat':str(row.get('vat') or '')[:40],
            'email':str(row.get('email') or '')[:254],'is_company':bool(row.get('is_company')),
            'country_id':remote_id(row.get('country_id')),'remote_id':row['id'],'remote_write_date':row.get('write_date') or None}
