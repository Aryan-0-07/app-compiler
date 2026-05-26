from pydantic import BaseModel
from typing import List, Optional

class Relation(BaseModel):
    from_entity: str
    to_entity: str
    type: str
    through: Optional[str] = None

class RolePermission(BaseModel):
    role: str
    can_create: List[str]
    can_read: List[str]
    can_update: List[str]
    can_delete: List[str]

class AppFlow(BaseModel):
    name: str
    steps: List[str]
    involves_payment: bool = False

class ArchOutput(BaseModel):
    entities: List[str]
    relations: List[Relation]
    role_permissions: List[RolePermission]
    flows: List[AppFlow]
    business_rules: List[str]
    page_list: List[str]