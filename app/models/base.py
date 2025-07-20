from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    org_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Mailbox(Base):
    __tablename__ = "mailboxes"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    address = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    webhook_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EmailMessage(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    mailbox_id = Column(String, ForeignKey("mailboxes.id"))
    sender = Column(String)
    subject = Column(String)
    body = Column(String)
    raw_content = Column(String)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
