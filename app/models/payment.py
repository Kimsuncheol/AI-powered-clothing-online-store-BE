import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class PaymentProvider(str, enum.Enum):
    PAYPAL = "PAYPAL"


class PaymentStatus(str, enum.Enum):
    CREATED = "CREATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    provider = Column(Enum(PaymentProvider), nullable=False, default=PaymentProvider.PAYPAL)
    provider_payment_id = Column(String(255), nullable=False, index=True)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.CREATED)
    raw_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    order = relationship("Order", backref="payments")
