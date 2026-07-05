from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.request_id import RequestIDMiddleware

app = FastAPI()
app.add_middleware(RequestIDMiddleware)


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"status": "ok"}


client = TestClient(app)


def test_generates_request_id_and_trace_id_when_absent() -> None:
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.headers["X-Trace-ID"]
    # No incoming trace id was supplied, so it defaults to the request id.
    assert response.headers["X-Trace-ID"] == response.headers["X-Request-ID"]


def test_echoes_incoming_request_id() -> None:
    response = client.get("/ping", headers={"X-Request-ID": "client-supplied-id"})
    assert response.headers["X-Request-ID"] == "client-supplied-id"


def test_echoes_incoming_trace_id_independently_of_request_id() -> None:
    response = client.get(
        "/ping",
        headers={"X-Request-ID": "req-1", "X-Trace-ID": "trace-1"},
    )
    assert response.headers["X-Request-ID"] == "req-1"
    assert response.headers["X-Trace-ID"] == "trace-1"


def test_two_requests_get_different_generated_ids() -> None:
    first = client.get("/ping").headers["X-Request-ID"]
    second = client.get("/ping").headers["X-Request-ID"]
    assert first != second
