from pydantic import BaseModel
from typing import List, Optional

class Permission(BaseModel):
    resource: str
    actions: List[str]

class Role(BaseModel):
    name: str
    description: str
    permissions: List[Permission]
    is_default: bool = False

class AuthSchema(BaseModel):
    roles: List[Role]
    jwt_enabled: bool = True
    session_expiry_hours: int = 24
    password_min_length: int = 8

    def get_role(self, name: str) -> Optional[Role]:
        return next((r for r in self.roles if r.name == name), None)

    def get_role_names(self) -> List[str]:
        return [r.name for r in self.roles]