import pytest

from app.services.schema_service import SchemaService


@pytest.mark.asyncio
async def test_discover_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        await SchemaService().discover("some-connection-id")
