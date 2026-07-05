import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_development_defaults_do_not_raise() -> None:
    Settings()  # backend_env defaults to "development" — must not raise


def test_invalid_backend_env_literal_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(backend_env="prod")  # typo/invalid — not one of the Literal values


def test_production_rejects_placeholder_secret_key() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY is still the placeholder default"):
        Settings(
            backend_env="production",
            secret_key="change-me-in-production",
            allowed_origins="https://app.example.com",
        )


def test_production_rejects_short_secret_key() -> None:
    with pytest.raises(ValidationError, match="at least 16"):
        Settings(
            backend_env="production",
            secret_key="short",
            allowed_origins="https://app.example.com",
        )


def test_production_rejects_empty_allowed_origins() -> None:
    with pytest.raises(ValidationError, match="ALLOWED_ORIGINS must be set"):
        Settings(
            backend_env="production",
            secret_key="a-sufficiently-long-real-secret-key",
            allowed_origins="",
        )


def test_production_warns_on_localhost_origin() -> None:
    with pytest.warns(UserWarning, match="wildcard or localhost origin"):
        Settings(
            backend_env="production",
            secret_key="a-sufficiently-long-real-secret-key",
            allowed_origins="http://localhost:3000",
        )


def test_production_warns_on_wildcard_origin() -> None:
    with pytest.warns(UserWarning, match="wildcard or localhost origin"):
        Settings(
            backend_env="production",
            secret_key="a-sufficiently-long-real-secret-key",
            allowed_origins="*",
        )


def test_production_with_safe_config_does_not_raise_or_warn(recwarn) -> None:
    Settings(
        backend_env="production",
        secret_key="a-sufficiently-long-real-secret-key",
        allowed_origins="https://app.example.com",
    )
    assert len(recwarn) == 0


def test_staging_env_is_not_subject_to_production_checks() -> None:
    # Same unsafe config as the production-rejection tests above, but staging
    # is deliberately not held to the production bar.
    Settings(backend_env="staging", secret_key="change-me-in-production", allowed_origins="")
