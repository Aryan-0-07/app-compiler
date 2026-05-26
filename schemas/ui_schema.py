from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ComponentType(str, Enum):
    TABLE = "table"
    FORM = "form"
    CARD = "card"
    CHART = "chart"
    NAVBAR = "navbar"
    SIDEBAR = "sidebar"
    BUTTON = "button"
    INPUT = "input"
    MODAL = "modal"

class UIField(BaseModel):
    name: str
    label: str
    component: ComponentType
    required: bool = False
    visible_to_roles: List[str] = []

class UIPage(BaseModel):
    name: str
    path: str
    requires_auth: bool = True
    allowed_roles: List[str] = []
    components: List[ComponentType]
    fields: List[UIField]
    api_calls: List[str]

class UISchema(BaseModel):
    pages: List[UIPage]
    layout: str
    theme: str = "light"