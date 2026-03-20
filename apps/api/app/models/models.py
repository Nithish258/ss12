import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Integer, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

class Decision(Base):
    __tablename__ = "decisions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String, nullable=False)
    context_prompt = Column(String, nullable=True)
    status = Column(String, default="DRAFT")
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    participants = relationship("Participant", back_populates="decision", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_decisions_creator_id", "creator_id"),
        Index("ix_decisions_status", "status"),
    )

class Participant(Base):
    __tablename__ = "participants"
    decision_id = Column(UUID(as_uuid=True), ForeignKey("decisions.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(String, nullable=False)
    has_submitted = Column(Boolean, default=False)

    decision = relationship("Decision", back_populates="participants")

    __table_args__ = (
        CheckConstraint("role IN ('owner', 'contributor', 'observer')", name="role_check"),
        Index("ix_participants_user_id", "user_id"),
    )

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("decisions.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    raw_reasoning = Column(String, nullable=False)
    confidence_score = Column(Integer, nullable=False)
    is_locked = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("decision_id", "user_id", name="uix_submission_decision_user"),
        Index("ix_submissions_decision_id", "decision_id"),
        Index("ix_submissions_user_id", "user_id"),
    )

class ExtractedArgument(Base):
    __tablename__ = "extracted_arguments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"))
    claim = Column(String, nullable=False)
    evidence = Column(String, nullable=True)
    implicit_assumption = Column(String, nullable=True)
    bias_flags = Column(JSON, nullable=True)
    strength_score = Column(Float, nullable=False)

class AiSynthesis(Base):
    __tablename__ = "ai_syntheses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("decisions.id"), unique=True)
    executive_summary = Column(String, nullable=True)
    argument_graph = Column(JSON, nullable=True)
    conflict_matrix = Column(JSON, nullable=True)
    blind_spots = Column(ARRAY(String), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True))
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=False)  # mapped to metadata column
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_audit_logs_entity_id", "entity_id"),
        Index("ix_audit_logs_actor_id", "actor_id"),
        Index("ix_audit_logs_timestamp", "timestamp"),
    )
