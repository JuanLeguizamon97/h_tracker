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
    # Extended billing fields
    client_code: Optional[str] = None
    salutation: Optional[str] = None
    first_name: Optional[str] = None
    middle_initial: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    main_phone: Optional[str] = None
    work_phone: Optional[str] = None
    mobile: Optional[str] = None
    main_email: Optional[str] = None
    street_address_1: Optional[str] = None
    street_address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    rep: Optional[str] = None
    payment_terms: Optional[str] = None
    team_member: Optional[str] = None
    notes: Optional[str] = None


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
    client_code: Optional[str] = None
    salutation: Optional[str] = None
    first_name: Optional[str] = None
    middle_initial: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    main_phone: Optional[str] = None
    work_phone: Optional[str] = None
    mobile: Optional[str] = None
    main_email: Optional[str] = None
    street_address_1: Optional[str] = None
    street_address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    rep: Optional[str] = None
    payment_terms: Optional[str] = None
    team_member: Optional[str] = None
    notes: Optional[str] = None


class ClientOut(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
