import os

import boto3

from chalice import Chalice, Cron

service_arn = os.getenv("APPRUNNER_ARN")
app = Chalice(app_name="openai-bot-scheduler")


@app.schedule(Cron("*", 10, "*", "*", "?", "*"))  # JST 19:00
def pause_service(event):
    client = boto3.client("apprunner")
    print(f"Pausing App Runner Service: {service_arn}")
    response = client.pause_service(ServiceArn=service_arn)
    return response


@app.schedule(Cron("*", 0, "*", "*", "?", "*"))  # JST 9:00
def resume_service(event):
    client = boto3.client("apprunner")
    print(f"Resuming App Runner Service: {service_arn}")
    response = client.resume_service(ServiceArn=service_arn)
    return response
