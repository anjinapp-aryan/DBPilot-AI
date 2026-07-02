class AIGatewayError(Exception):
    """Raised only when every configured provider has failed (total outage).

    Carries the ordered list of provider display names that were attempted so
    the API layer can return a structured error to the client instead of
    leaking a stack trace. Never raised while at least one provider in the
    chain can still serve the request.
    """

    def __init__(self, message: str, provider_attempts: list[str] | None = None) -> None:
        super().__init__(message)
        self.provider_attempts = provider_attempts or []


class QuotaExceededError(Exception):
    """Raised when a provider responds with 429 (rate limit / quota exhausted).

    Kept distinct from generic transport errors so the gateway can skip retry
    budget on a rate-limited provider and fail over immediately.
    """
