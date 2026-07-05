"""Standard API response envelope.

Every route returns this shape on success:
    {"success": true, "data": {...}, "metadata": {...}, "timestamp": "..."}

Error responses use a matching but distinct shape built in
app/middleware/exceptions.py (`{"success": false, "error": {...},
"timestamp": "..."}`) — errors never have a `data`/`metadata` field, so
they're deliberately not built on this same generic model.
"""

from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
