import hmac
import hashlib
import json

from fastapi import HTTPException, Request, status

from config import get_settings

async def verify_signature(request: Request, body: bytes):
    """
    Verifies the signature of the webhook request.
    """
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Hub-Signature-256 header missing."
        )

    try:
        secret_bytes = get_settings().WEBHOOK_SECRET.encode('utf-8')
        mac = hmac.new(secret_bytes, body, hashlib.sha256)
        expected_signature = "sha256=" + mac.hexdigest()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate signature."
        )

    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Webhook signature verification failed."
        )
    
def parse_webhook_payload(body: bytes):
    """
    Parses the webhook payload.
    """
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload."
        )

def get_event_type(request: Request):
    """
    Returns the event type of the webhook request.
    """
    event_type = request.headers.get("X-GitHub-Event")
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-GitHub-Event header missing."
        )

    return event_type
