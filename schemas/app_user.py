from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AppUserOut(BaseModel):
    id: str
    azure_oid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
