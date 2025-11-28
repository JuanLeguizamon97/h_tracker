from pydantic import BaseModel
from typing import List, Dict

class EmployeeProfile(BaseModel):
    employee_id: int
    employee_name: str
    employee_email: str
    password: str

    class Config:
        rom_attributes = True