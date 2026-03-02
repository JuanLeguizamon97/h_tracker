# schemas/user_roles.py
from pydantic import BaseModel, ConfigDict


class UserRoleBase(BaseModel):
    user_id: str
    role: str


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    role: str


class UserRoleOut(UserRoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
