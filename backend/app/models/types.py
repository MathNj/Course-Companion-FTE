"""
Custom SQLAlchemy Types

Provides custom type definitions for UUID and JSON columns.
"""

from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSON as PostgresJSON
from sqlalchemy.types import VARCHAR, JSON as SQLAlchemyJSON


class UUID(TypeDecorator):
    """
    UUID type that works with both PostgreSQL and other databases.

    Uses PostgreSQL UUID type when available, falls back to VARCHAR(36).
    """
    impl = VARCHAR
    cache_ok = True

    def __init__(self, *args, **kwargs):
        """
        Accept and ignore common UUID parameters like 'as_uuid'.

        Our custom type already handles UUID conversion automatically via
        process_bind_param and process_result_value.
        """
        # Remove 'as_uuid' from kwargs if present to prevent errors
        kwargs.pop('as_uuid', None)
        super().__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        """Use PostgreSQL UUID type if available."""
        if dialect.name == "postgresql":
            # Use the PostgreSQL native UUID type with as_uuid=False
            return PostgresUUID(as_uuid=False)
        else:
            return VARCHAR(36)

    def process_bind_param(self, value, dialect):
        """Process Python UUID for database storage."""
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        """Convert database value back to Python UUID."""
        if value is None:
            return value
        import uuid
        try:
            return uuid.UUID(value)
        except (ValueError, AttributeError):
            return value


class JSON(TypeDecorator):
    """
    JSON type that works with both PostgreSQL and other databases.

    Uses PostgreSQL JSON type when available, falls back to SQLAlchemy JSON.
    """
    impl = SQLAlchemyJSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Use PostgreSQL JSON type if available."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresJSON())
        else:
            return dialect.type_descriptor(SQLAlchemyJSON())
