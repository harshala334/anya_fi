"""SQLAlchemy database models for Anya.fi."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    ForeignKey, Boolean, Text, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class GoalStatus(str, enum.Enum):
    """Goal status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class GoalType(str, enum.Enum):
    """Goal type enumeration."""
    SAVING = "saving"
    PURCHASE = "purchase"
    EMERGENCY_FUND = "emergency_fund"
    DEBT_PAYOFF = "debt_payoff"


class TransactionCategory(str, enum.Enum):
    """Transaction category enumeration."""
    SHOPPING = "shopping"
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    TRANSPORT = "transport"
    BILLS = "bills"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    OTHER = "other"


class ConsentStatus(str, enum.Enum):
    """Account Aggregator consent status."""
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("ConversationSession", back_populates="user", cascade="all, delete-orphan")
    aa_consents = relationship("AAConsent", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.name})>"


class Goal(Base):
    """Financial goal model."""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    goal_type = Column(SQLEnum(GoalType), default=GoalType.SAVING)
    title = Column(String, nullable=False)  # e.g., "Buy a laptop"
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    
    # Budget allocation
    month_nonessential_budget = Column(Float, nullable=True)  # Monthly budget for non-essentials
    
    deadline = Column(DateTime, nullable=True)
    status = Column(SQLEnum(GoalStatus), default=GoalStatus.ACTIVE)
    
    # Optional: Image/visualization
    thumbnail_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    
    def __repr__(self):
        return f"<Goal(id={self.id}, title={self.title}, target={self.target_amount})>"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate goal progress as percentage."""
        if self.target_amount == 0:
            return 0.0
        return (self.current_amount / self.target_amount) * 100


class Transaction(Base):
    """Transaction model."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    merchant = Column(String, nullable=False)
    category = Column(SQLEnum(TransactionCategory), default=TransactionCategory.OTHER)
    is_essential = Column(Boolean, default=False)
    
    # Account Aggregator reference
    aa_transaction_id = Column(String, nullable=True, unique=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, merchant={self.merchant})>"


class ConversationSession(Base):
    """Conversation session for maintaining context."""
    __tablename__ = "conversation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session state
    context = Column(Text, nullable=True)  # JSON string of conversation context
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<ConversationSession(id={self.id}, user_id={self.user_id})>"


class AAConsent(Base):
    """Account Aggregator consent tracking."""
    __tablename__ = "aa_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    consent_handle = Column(String, unique=True, nullable=False)
    status = Column(SQLEnum(ConsentStatus), default=ConsentStatus.PENDING)
    
    # Consent details
    granted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="aa_consents")
    
    def __repr__(self):
        return f"<AAConsent(id={self.id}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if consent is currently active."""
        if self.status != ConsentStatus.ACTIVE:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
