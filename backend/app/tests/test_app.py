from chalice.test import Client

from app import app


def test_health():
    with Client(app) as client:
        response = client.http.get("/_health")
        assert response.json_body == {"status": "ok"}
