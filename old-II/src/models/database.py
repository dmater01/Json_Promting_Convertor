"""SQLAlchemy database models."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class APIKey(Base):
    """API key model for authentication."""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    team = Column(String(255))
    rate_limit_per_hour = Column(Integer, default=1000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    request_logs = relationship("RequestLog", back_populates="api_key")

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name={self.name})>"


class RequestLog(Base):
    """Request log model for tracking API usage."""

    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"))
    prompt_text = Column(Text, nullable=False)
    prompt_length = Column(Integer)
    request_params = Column(JSON)
    response_data = Column(JSON)
    validation_status = Column(String(50))
    provider_used = Column(String(50), index=True)
    processing_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    cached = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    api_key = relationship("APIKey", back_populates="request_logs")

    def __repr__(self) -> str:
        return f"<RequestLog(id={self.id}, request_id={self.request_id})>"


class Schema(Base):
    """Schema model for storing JSON schemas."""

    __tablename__ = "schemas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    schema_definition = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    is_public = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Schema(id={self.id}, name={self.name}, version={self.version})>"


class PromptTemplate(Base):
    """Prompt template model for reusable prompts."""

    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    template_text = Column(Text, nullable=False)
    parameters = Column(JSON)  # List of required parameters
    example_usage = Column(JSON)
    schema_id = Column(UUID(as_uuid=True), ForeignKey("schemas.id"), nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    schema = relationship("Schema")

    def __repr__(self) -> str:
        return f"<PromptTemplate(id={self.id}, name={self.name})>"


class Job(Base):
    """Job model for asynchronous processing."""

    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"))
    job_type = Column(String(50), nullable=False)  # 'analyze', 'batch', etc.
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    request_params = Column(JSON, nullable=False)
    result = Column(JSON)
    error_message = Column(Text)
    webhook_url = Column(String(500))
    webhook_status = Column(String(50))
    created_at = Column(DateTime, server_default=func.now(), index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)  # Auto-calculated as created_at + 24 hours

    # Relationships
    api_key = relationship("APIKey")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status})>"
