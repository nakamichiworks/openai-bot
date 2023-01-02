# Template for Slackbot development with Bolt and AWS Chalice


## Requirements

- Python 3.9
- Poetry


## Preparation

1. Set your project and app names in the following files.
     - `pyproject.tom` (`name`)
     - `app/app.py` (`app_name`)
     - `app/.chalice/config.template.json` (`app_name`)

2. Install python packages by `poetry install`.

3. Create your slack app, install it to your slack workspace, and get the bot token and signing secret. For details, read [the official tutorial](https://slack.dev/bolt-python/tutorial/getting-started-http).

## Development

- poetry for package management
- pysen for linting and formatting
- pytest for testing

## Deployment
Run the deployment script.

- Development environment

    ```bash
    export SLACK_BOT_TOKEN_DEV=<your-dev-bot-token>
    export SLACK_SIGNING_SECRET_DEV=<your-dev-signing-secret>
    ./deploy.sh dev
    ```

- Production environment

    ```bash
    export SLACK_BOT_TOKEN=<your-bot-token>
    export SLACK_SIGNING_SECRET=<your-signing-secret>
    ./deploy.sh prod
    ```

After the first deployment, properly configure the settings below. Follow [the official tutorial](https://slack.dev/bolt-python/tutorial/getting-started-http#setting-up-events) for details.

- Interactivity & Shortcuts Request URL
- Event Subscriptions Request URL
- Subscribed bot events (`app_mention`, `message.channels`, etc.)
