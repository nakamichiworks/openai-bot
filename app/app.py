from chalice import Chalice
from loguru import logger
from slack_bolt.adapter.aws_lambda.chalice_handler import ChaliceSlackRequestHandler

from chalicelib.slack import app as bolt_app

app = Chalice(app_name="app")
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
    logger.debug(f"Request: {request.to_dict()}")
    response = slack_handler.handle(request)
    logger.debug(f"Response: {response.to_dict()}")
    return response
