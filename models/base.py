from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData, Table, Column
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    metadata = MetaData(schema="public")

# Stub for Supabase-managed auth.users — not created or dropped by Alembic,
# only registered so SQLAlchemy can resolve cross-schema FK references.
Table(
    "users",
    Base.metadata,
    Column("id", UUID),
    schema="auth",
    keep_existing=True,
)