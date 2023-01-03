from chalice import Chalice
from slack_bolt.adapter.aws_lambda.chalice_handler import ChaliceSlackRequestHandler

from chalicelib.slack import bolt_app

app = Chalice(app_name="openai-bot")
slack_handler = ChaliceSlackRequestHandler(bolt_app, app)
slack_handler.clear_all_log_handlers()


@app.route("/_health")
def health():
    return {"status": "ok"}


@app.route(
    "/slack/events",
    methods=["POST"],
    content_types=["application/x-www-form-urlencoded", "application/json"],
)
def slack_events():
    request = app.current_request
    if request.headers.get("X-Slack-Retry-Num") is not None:
        return {"status": "retry request ignored"}
    response = slack_handler.handle(request)
    return response
