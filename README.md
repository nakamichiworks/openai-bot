# OpenAI Bot for Slack


## Requirements

- Python 3.9
- Poetry


## Preparation

1. Install python packages by `poetry install`.

2. Create your slack app, install it to your slack workspace, and get the bot token and signing secret. For details, read [the official tutorial](https://slack.dev/bolt-python/tutorial/getting-started-http).


## Deployment
Run the deployment script.

- Development environment

    ```bash
    export SLACK_BOT_TOKEN_DEV=<your-dev-bot-token>
    export SLACK_SIGNING_SECRET_DEV=<your-dev-signing-secret>
    export OPENAI_ORGANIZATION=<your-org>
    export OPENAI_API_KEY=<your-api-key>
    ./deploy.sh dev
    ```

- Production environment

    ```bash
    export SLACK_BOT_TOKEN=<your-bot-token>
    export SLACK_SIGNING_SECRET=<your-signing-secret>
    export OPENAI_ORGANIZATION=<your-org>
    export OPENAI_API_KEY=<your-api-key>
    ./deploy.sh prod
    ```

After the first deployment, properly configure the settings below. Follow [the official tutorial](https://slack.dev/bolt-python/tutorial/getting-started-http#setting-up-events) for details.

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
