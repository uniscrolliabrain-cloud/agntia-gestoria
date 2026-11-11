import uuid

# Contrato estable de errores (tarea 56): cada código que el adaptador puede
# emitir tiene una categoría y una acción siguiente distintas. Un cliente no
# debe inferir la acción a partir del texto ni del HTTP status.
#   code -> (categoría, siguiente acción)
CONTRACT={
    'approval_required':('permission','request_human_approval'),
    'attachment_changed':('conflict','review_attachment'),
    'binding_conflict':('conflict','review_binding'),
    'circuit_open':('provider','retry_later'),
    'configuration':('configuration','fix_configuration'),
    'configuration_changed':('conflict','review_binding'),
    'conflict':('conflict','review_conflict'),
    'connection_changed':('conflict','review_conflict'),
    'disabled':('configuration','enable_adapter'),
    'evidence_required':('validation','review_evidence'),
    'expired':('conflict','request_new_approval'),
    'forbidden':('permission','request_access'),
    'idempotency_conflict':('conflict','review_conflict'),
    'identity_confirmation_required':('configuration','review_binding'),
    'integrity':('conflict','review_evidence'),
    'invalid_attachment':('validation','review_attachment'),
    'invalid_response':('provider','report_with_correlation_id'),
    'lease_lost':('provider','retry_later'),
    'limit':('limit','reduce_batch'),
    'malware_scan_failed':('validation','review_attachment'),
    'mapping_blocked':('validation','review_mapping'),
    'network':('network','retry_later'),
    'network_policy':('configuration','fix_configuration'),
    'not_configured':('configuration','fix_configuration'),
    'not_found':('not_found','none'),
    'not_ready':('configuration','review_binding'),
    'principal_revoked':('authentication','reauthenticate'),
    'provider_auth':('provider','fix_configuration'),
    'provider_unavailable':('provider','retry_later'),
    'provider_validation':('provider','correct_request'),
    'rate_limit':('limit','retry_later'),
    'redirect_blocked':('network','fix_configuration'),
    'remote_totals_mismatch':('conflict','reconcile_write'),
    'response_too_large':('provider','reduce_batch'),
    'retry_budget':('limit','review_conflict'),
    'scanner_required':('configuration','fix_configuration'),
    'scanner_unavailable':('configuration','fix_configuration'),
    'scope_violation':('permission','request_access'),
    'source_changed':('conflict','refresh_source'),
    'stale_capabilities':('configuration','revalidate_connection'),
    'timeout':('provider','reconcile_write'),
    'totals_mismatch':('conflict','review_conflict'),
    'unsafe_principal':('authentication','reauthenticate'),
    'unsafe_remote_result':('provider','reconcile_write'),
    'unsupported':('unsupported','reduce_scope'),
    'unsupported_attachment':('unsupported','reduce_scope'),
    'validation':('validation','correct_request'),
}
FALLBACK=('integration','report_with_correlation_id')


def contract(code):
    """Categoría y acción siguiente para un código; nunca inventa privilegios."""
    return CONTRACT.get(code,FALLBACK)


class IntegrationError(Exception):
    """Only deliberately safe strings may be stored here, never provider payloads."""
    def __init__(self, code, message, status=400, retryable=False, uncertain=False):
        super().__init__(message)
        self.code=code;self.message=message;self.status=status
        self.retryable=retryable;self.uncertain=uncertain

    def public(self, correlation_id=None):
        category,action=contract(self.code)
        if self.uncertain:
            action='reconcile_write'
        elif self.code=='timeout':
            action='retry_later'
        return {'code':self.code,'message':self.message,'correlation_id':correlation_id or str(uuid.uuid4()),'retryable':self.retryable,'reconciliation_required':self.uncertain,'category':category,'next_action':action}


def reject(code,message,status=400):raise IntegrationError(code,message,status)
