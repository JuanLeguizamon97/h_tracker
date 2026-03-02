# schemas/clients.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ClientBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None
    manager_phone: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None
    manager_phone: Optional[str] = None


class ClientOut(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
