from config.database import Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid


class UserRole(Base):

    __tablename__ = "user_roles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("employees.id"), nullable=False)
    role = Column(String, nullable=False, default="employee")

    employee = relationship("Employee")
