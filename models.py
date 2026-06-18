from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey

Base = declarative_base()

class UserRoleModel(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "ticketing"} # Aligns with your connection.py schema setup

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)


class TicketReplyModel(Base):
    __tablename__ = "ticket_replies"
    __table_args__ = {"schema": "ticketing"}

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("ticketing.tickets.id", ondelete="CASCADE"), nullable=False)
    author_email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    email_sent = Column(Boolean, default=False)

class TicketModel(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": "ticketing"}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="open")
    urgency = Column(String(20), default="medium")
    creator_email = Column(String(255))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    assigned_to = Column(String, nullable=True)