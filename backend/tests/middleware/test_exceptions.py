from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.ai.exceptions import AIGatewayError
from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    DatabaseException,
    SchemaDiscoveryException,
    ValidationException,
)
from app.middleware.exceptions import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)


class Body(BaseModel):
    name: str


@app.get("/boom/validation")
def boom_validation() -> None:
    raise ValidationException("bad input", details=[{"field": "name"}])


@app.get("/boom/database")
def boom_database() -> None:
    raise DatabaseException("connection refused")


@app.get("/boom/schema")
def boom_schema() -> None:
    raise SchemaDiscoveryException("introspection failed")


@app.get("/boom/auth")
def boom_auth() -> None:
    raise AuthenticationException("missing credentials")


@app.get("/boom/authz")
def boom_authz() -> None:
    raise AuthorizationException("not allowed")


@app.get("/boom/ai-gateway")
def boom_ai_gateway() -> None:
    raise AIGatewayError("all providers down", ["DeepSeek", "Groq"])


@app.get("/boom/generic")
def boom_generic() -> None:
    raise RuntimeError("something broke internally, full of secrets")


@app.get("/boom/not-found")
def boom_not_found() -> None:
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="not found")


@app.post("/echo")
def echo(body: Body) -> Body:
    return body


client = TestClient(app, raise_server_exceptions=False)


def test_validation_exception_returns_422_envelope() -> None:
    response = client.get("/boom/validation")
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"] == {
        "code": "validation_error",
        "message": "bad input",
        "details": [{"field": "name"}],
    }
    assert "timestamp" in body


def test_database_exception_returns_503() -> None:
    response = client.get("/boom/database")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "database_error"


def test_schema_discovery_exception_returns_502() -> None:
    response = client.get("/boom/schema")
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "schema_discovery_error"


def test_authentication_exception_returns_401() -> None:
    response = client.get("/boom/auth")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_error"


def test_authorization_exception_returns_403() -> None:
    response = client.get("/boom/authz")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "authorization_error"


def test_ai_gateway_error_returns_503_with_provider_attempts() -> None:
    response = client.get("/boom/ai-gateway")
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "ai_provider_error"
    assert body["error"]["details"] == [{"providerAttempts": ["DeepSeek", "Groq"]}]


def test_request_validation_error_returns_422_with_pydantic_errors() -> None:
    response = client.post("/echo", json={"wrong_field": 1})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert len(body["error"]["details"]) >= 1


def test_starlette_http_exception_preserves_status_code() -> None:
    response = client.get("/boom/not-found")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["message"] == "not found"


def test_unhandled_exception_returns_generic_500_without_leaking_internals() -> None:
    response = client.get("/boom/generic")
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert body["error"]["message"] == "An unexpected error occurred"
    assert "secrets" not in response.text
