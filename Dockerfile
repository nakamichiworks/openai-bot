FROM python:3.10.9-slim-bullseye

WORKDIR /code

ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && \
    apt-get install --no-install-recommends -y curl && \
    curl -sSL https://install.python-poetry.org/ | python -

COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
RUN poetry config virtualenvs.create false && \
    poetry install --only main

RUN curl -sSL https://install.python-poetry.org | python3 - --uninstall && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    apt-get clean

COPY ./app /code/app

EXPOSE 80
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]
