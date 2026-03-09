from config.database import Base
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class Client(Base):

    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    manager_name = Column(String, nullable=True)
    manager_email = Column(String, nullable=True)
    manager_phone = Column(String, nullable=True)
    # Extended billing fields
    client_code = Column(String, nullable=True)
    salutation = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    middle_initial = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    main_phone = Column(String, nullable=True)
    work_phone = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    main_email = Column(String, nullable=True)
    street_address_1 = Column(String, nullable=True)
    street_address_2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip = Column(String, nullable=True)
    country = Column(String, nullable=True)
    rep = Column(String, nullable=True)
    payment_terms = Column(String, nullable=True)
    team_member = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    projects = relationship("Project", back_populates="client")
