from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi import SlackRequestHandler

from .lib.slack import bolt_app

app = FastAPI()
slack_handler = SlackRequestHandler(bolt_app)


@app.get("/_health")
async def health():
    return {"status": "ok"}


@app.post("/slack/events")
async def slack_events(request: Request):
    if request.headers.get("X-Slack-Retry-Num") is not None:
        return {"status": "retry request ignored"}
    response = await slack_handler.handle(request)
    return response
