from fastapi import FastAPI
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.exceptions import RateLimitException
from app.middleware.exceptions import _error_response

# A dedicated low-limit Limiter/app — the real app's default (60/minute,
# app.middleware.rate_limit.limiter) would need 61 requests per test to
# trip deterministically. This exercises the exact same mechanics (same
# Limiter class, same SlowAPIMiddleware, same sync exception-handler
# requirement) against a limit small enough to hit in 2-3 requests.
test_limiter = Limiter(key_func=get_remote_address, default_limits=["2/minute"])

app = FastAPI()
app.state.limiter = test_limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def handle_rate_limit_exceeded(request, exc):  # noqa: ANN001, ANN201 - mirrors the real handler
    return _error_response(
        RateLimitException.status_code,
        RateLimitException.code,
        "Rate limit exceeded — please slow down.",
        details=[{"limit": str(exc.detail)}],
    )


@app.get("/limited")
def limited() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/exempt")
@test_limiter.exempt
def exempt() -> dict[str, str]:
    return {"status": "ok"}


client = TestClient(app)


def setup_function() -> None:
    test_limiter.reset()


def test_allows_requests_within_the_limit() -> None:
    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200


def test_returns_429_with_standard_envelope_once_limit_exceeded() -> None:
    client.get("/limited")
    client.get("/limited")
    response = client.get("/limited")

    assert response.status_code == 429
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "rate_limit_exceeded"
    assert "timestamp" in body


def test_exempt_route_is_never_rate_limited() -> None:
    for _ in range(5):
        assert client.get("/exempt").status_code == 200
