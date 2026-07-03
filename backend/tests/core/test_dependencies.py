from app.ai.factory import get_ai_gateway
from app.ai.service import AIGatewayService
from app.core.cache import InMemoryCache
from app.core.config import Settings
from app.core.dependencies import get_cache, get_config, get_llm_gateway, get_schema_service
from app.services.schema_service import SchemaService


def setup_function() -> None:
    get_ai_gateway.cache_clear()


def test_get_config_returns_settings_instance() -> None:
    assert isinstance(get_config(), Settings)


def test_get_llm_gateway_returns_the_same_singleton_as_the_factory() -> None:
    assert get_llm_gateway() is get_ai_gateway()


def test_get_llm_gateway_returns_ai_gateway_service_instance() -> None:
    assert isinstance(get_llm_gateway(), AIGatewayService)


def test_get_cache_returns_a_stable_singleton() -> None:
    first = get_cache()
    second = get_cache()
    assert first is second
    assert isinstance(first, InMemoryCache)


def test_get_schema_service_returns_a_stable_singleton() -> None:
    first = get_schema_service()
    second = get_schema_service()
    assert first is second
    assert isinstance(first, SchemaService)
