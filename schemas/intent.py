from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class FeatureCategory(str, Enum):
    AUTH = "auth"
    CRUD = "crud"
    DASHBOARD = "dashboard"
    PAYMENTS = "payments"
    NOTIFICATIONS = "notifications"
    SEARCH = "search"
    ANALYTICS = "analytics"
    FILE_UPLOAD = "file_upload"
    OTHER = "other"

class Feature(BaseModel):
    name: str
    category: FeatureCategory
    description: str
    requires_auth: bool = True

class Entity(BaseModel):
    name: str
    description: str
    is_primary: bool = False
    has_ownership: bool = False

class ClarificationRequest(BaseModel):
    questions: List[str]
    reason: str

class IntentOutput(BaseModel):
    app_name: str
    app_description: str
    entities: List[Entity]
    roles: List[str]
    features: List[Feature]
    auth_required: bool
    payment_required: bool
    multi_tenant: bool = False
    assumptions: List[str]
    clarification_needed: Optional[ClarificationRequest] = None