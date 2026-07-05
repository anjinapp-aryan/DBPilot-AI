"""Rate limiting (slowapi).

In-memory storage by default — fine for a single-process deployment.
Swap `storage_uri` to a Redis URI for multi-worker deployments without
touching call sites, same "start simple behind an interface" approach as
app/core/cache.py.

The global default limit applies to every route automatically via
SlowAPIMiddleware (wired in app/main.py) — routes that shouldn't be
rate-limited at all (health checks, hit frequently by orchestrators) are
marked with @limiter.exempt, not given a higher limit.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

limiter = Limiter(key_func=get_remote_address, default_limits=[get_settings().rate_limit_default])
