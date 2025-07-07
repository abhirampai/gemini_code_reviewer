from fastapi import APIRouter, Request

from utils.webhook import verify_signature, parse_webhook_payload, get_event_type
from models.pull_request import PullRequest

router = APIRouter(tags=["webhook"])


@router.post("/webhook")
async def webhook(request: Request):
    """
    Receives GitHub webhook events.
    """
    body = await request.body()
    await verify_signature(request, body)
    payload = parse_webhook_payload(body)
    event_type = get_event_type(request)
    if event_type == "pull_request":
        pull_request = PullRequest.from_github_event(payload)
        if (
            payload.get("action") == "open"
            or payload.get("action") == "reopened"
            or payload.get("action") == "synchronize"
        ):
            print(f'Executing gemini review on pull request: {pull_request.repository["full_name"]}#{pull_request.number}')
            pull_request.gemini_review_request()
    elif event_type == "ping":
        return {"message": "pong"}
    else:
        return {"message": f"Event type '{event_type}' received but not handled."}

    return {"message": "Webhook received"}
