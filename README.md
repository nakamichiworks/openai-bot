# OpenAI Bot for Slack


## Requirements

- Python 3.9
- Poetry


## Preparation

1. Install python packages by `poetry install`.

2. Create your slack app, install it to your slack workspace, and get the bot token and signing secret. For details, read [the Slack official tutorial](https://slack.dev/bolt-python/tutorial/getting-started-http).

## Development

You can run a development server by the following command.

```bash
./scripts/run_dev_server.sh
```

## Deployment

The app is deployed to AWS AppRunner by using [`copilot`](https://aws.github.io/copilot-cli/) command.

```bash
./scripts/update_manifest.sh
copilot svc deploy
```

After the first deployment, properly configure the settings below. Follow [the Slack official tutorial](https://slack.dev/bolt-python/tutorial/getting-started-http#setting-up-events) for details.

- Interactivity & Shortcuts Request URL
- Event Subscriptions Request URL
- Subscribed events
  - `app_mention`
  - `message.channels`
  - `file_shared`
- OAuth scopes
  - `chat:write`
  - `files:write`
  - `files:read`
  - `search:read`
