from config.database import Base
from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime, timezone
import uuid


class AppUser(Base):

    __tablename__ = "app_users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    azure_oid = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
