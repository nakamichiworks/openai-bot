# Slack message subtype matchers
# https://slack.dev/bolt-python/concepts#listener-middleware


def match_message_replied(event) -> bool:
    # subtype can be empty https://api.slack.com/events/message/message_replied
    condition1 = event.get("subtype") == "message_replied"
    ts = event.get("ts")
    thread_ts = event.get("thread_ts")
    condition2 = ts and thread_ts and ts != thread_ts
    return condition1 or condition2


def match_file_share(event) -> bool:
    return event.get("subtype") == "file_share"
