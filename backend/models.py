from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

# ─── مشتریان ──────────────────────────────────
class Customer(Base):
    __tablename__ = "customers"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    business    = Column(String(100), nullable=False)
    phone       = Column(String(20), unique=True, nullable=False)
    category    = Column(String(50), nullable=False)
    api_key     = Column(String(100), unique=True, nullable=False)
    is_active   = Column(Boolean, default=True)
    plan        = Column(String(20), default="basic")  # basic, pro, enterprise
    expires_at  = Column(DateTime, nullable=True)
    created_at  = Column(DateTime, default=datetime.now)

    # روابط
    messages    = relationship("Message", back_populates="customer")
    payments    = relationship("Payment", back_populates="customer")

# ─── پیام‌ها ───────────────────────────────────
class Message(Base):
    __tablename__ = "messages"

    id           = Column(Integer, primary_key=True, index=True)
    customer_id  = Column(Integer, ForeignKey("customers.id"))
    user_id      = Column(String(50), nullable=False)
    role         = Column(String(10), nullable=False)  # user/assistant
    content      = Column(Text, nullable=False)
    category     = Column(String(50), nullable=False)
    tokens       = Column(Integer, default=0)
    created_at   = Column(DateTime, default=datetime.now)

    customer     = relationship("Customer", back_populates="messages")

# ─── پرداخت‌ها ─────────────────────────────────
class Payment(Base):
    __tablename__ = "payments"

    id           = Column(Integer, primary_key=True, index=True)
    customer_id  = Column(Integer, ForeignKey("customers.id"))
    amount       = Column(Float, nullable=False)
    plan         = Column(String(20), nullable=False)
    status       = Column(String(20), default="pending")  # pending/success/failed
    ref_id       = Column(String(100), nullable=True)
    created_at   = Column(DateTime, default=datetime.now)

    customer     = relationship("Customer", back_populates="payments")

# ─── ادمین ────────────────────────────────────
class Admin(Base):
    __tablename__ = "admins"

    id           = Column(Integer, primary_key=True, index=True)
    username     = Column(String(50), unique=True, nullable=False)
    password     = Column(String(200), nullable=False)
    created_at   = Column(DateTime, default=datetime.now)
