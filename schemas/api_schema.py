from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class APIField(BaseModel):
    name: str
    type: str
    required: bool = True
    maps_to_db_column: Optional[str] = None

class APIEndpoint(BaseModel):
    name: str
    method: HTTPMethod
    path: str
    description: str
    requires_auth: bool = True
    allowed_roles: List[str] = []
    request_fields: List[APIField] = []
    response_fields: List[APIField]
    db_table: Optional[str] = None

class APISchema(BaseModel):
    endpoints: List[APIEndpoint]
    base_path: str = "/api"
    auth_endpoint: str = "/api/auth/login"