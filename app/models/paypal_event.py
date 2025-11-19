from sqlalchemy import Column, DateTime, Integer, JSON, String, func

from app.db.base_class import Base


class PayPalEvent(Base):
    __tablename__ = "paypal_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(255), unique=True, nullable=False, index=True)
    event_type = Column(String(255), nullable=False)
    payload = Column(JSON, nullable=False)
    processed_at = Column(DateTime, server_default=func.now(), nullable=False)
