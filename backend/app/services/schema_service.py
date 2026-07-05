"""Schema Discovery service — placeholder.

Deliberately unimplemented: Phase 2 (Schema Discovery) has not started.
This class exists now only so the DI container has a stable slot
(``get_schema_service``) for routes/tests to depend on; Phase 2 fills in
the actual introspection logic here without callers needing to change how
they obtain a SchemaService.
"""


class SchemaService:
    async def discover(self, connection_id: str) -> None:
        raise NotImplementedError("Schema discovery is not implemented yet (lands in Phase 2)")
