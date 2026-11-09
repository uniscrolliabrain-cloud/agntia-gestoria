import uuid


class IntegrationError(Exception):
    """Only deliberately safe strings may be stored here, never provider payloads."""
    def __init__(self, code, message, status=400, retryable=False, uncertain=False):
        super().__init__(message)
        self.code=code;self.message=message;self.status=status
        self.retryable=retryable;self.uncertain=uncertain

    def public(self, correlation_id=None):
        return {'code':self.code,'message':self.message,'correlation_id':correlation_id or str(uuid.uuid4()),'retryable':self.retryable,'reconciliation_required':self.uncertain}


def reject(code,message,status=400):raise IntegrationError(code,message,status)
