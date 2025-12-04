# schemas/clients.py
from pydantic import BaseModel
from typing import Optional


class ClientBase(BaseModel):
    client_name: str
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    billing_address_line1: Optional[str] = None
    billing_address_line2: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postal_code: Optional[int] = None
    billing_country: Optional[str] = None
    active: bool = True


class ClientCreate(ClientBase):
    # Si no los envías, se usarán los defaults de la BD (uuid)
    primary_id_client: Optional[str] = None
    second_id_client: Optional[str] = None


class ClientUpdate(BaseModel):
    # Todos opcionales para permitir actualizaciones parciales
    client_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    billing_address_line1: Optional[str] = None
    billing_address_line2: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postal_code: Optional[int] = None
    billing_country: Optional[str] = None
    active: Optional[bool] = None


class ClientOut(ClientBase):
    primary_id_client: str
    second_id_client: str

    class Config:
        from_attributes = True  # Pydantic v2 (equivalente a orm_mode=True en v1)
