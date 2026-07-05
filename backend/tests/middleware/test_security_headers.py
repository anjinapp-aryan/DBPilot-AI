from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.security_headers import SecurityHeadersMiddleware

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"status": "ok"}


client = TestClient(app)


def test_sets_conservative_default_headers() -> None:
    response = client.get("/ping")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Permissions-Policy"] == "geolocation=(), camera=(), microphone=()"


def test_no_hsts_header_over_plain_http() -> None:
    response = client.get("/ping")
    assert "Strict-Transport-Security" not in response.headers


def test_hsts_header_present_when_forwarded_proto_is_https() -> None:
    response = client.get("/ping", headers={"X-Forwarded-Proto": "https"})
    assert response.headers["Strict-Transport-Security"] == "max-age=63072000; includeSubDomains"
