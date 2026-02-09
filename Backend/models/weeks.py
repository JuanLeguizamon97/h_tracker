from config.database import Base
from sqlalchemy import Column, Integer, Boolean, Date
from sqlalchemy.orm import relationship

class Week(Base):

    __tablename__ = "weeks"

    week_start = Column(Date, primary_key=True)
    week_end = Column(Date, nullable=False)
    week_number = Column(Integer, nullable=False)
    year_number = Column(Integer, nullable=False)
    is_split_month = Column(Boolean, nullable=False, default=False)
    month_a_key = Column(Integer, nullable=True) 
    month_b_key = Column(Integer, nullable=True)  
    qty_days_a = Column(Integer, nullable=True)
    qty_days_b = Column(Integer, nullable=True)

    time_entries = relationship("TimeEntry", back_populates="week")

