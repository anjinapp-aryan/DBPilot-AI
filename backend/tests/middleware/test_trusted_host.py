from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.testclient import TestClient

app = FastAPI()
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["allowed.example.com"])


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"status": "ok"}


client = TestClient(app)


def test_allowed_host_passes() -> None:
    response = client.get("/ping", headers={"Host": "allowed.example.com"})
    assert response.status_code == 200


def test_disallowed_host_is_rejected() -> None:
    response = client.get("/ping", headers={"Host": "evil.example.com"})
    assert response.status_code == 400
