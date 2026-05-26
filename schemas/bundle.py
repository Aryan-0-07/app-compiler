from pydantic import BaseModel
from typing import List, Optional
from schemas.ui_schema import UISchema
from schemas.api_schema import APISchema
from schemas.db_schema import DBSchema
from schemas.auth_schema import AuthSchema

class ValidationIssue(BaseModel):
    layer: str
    severity: str
    message: str
    field: Optional[str] = None

class SchemaBundle(BaseModel):
    ui: UISchema
    api: APISchema
    db: DBSchema
    auth: AuthSchema
    validation_issues: List[ValidationIssue] = []
    repair_attempts: int = 0
    is_valid: bool = False

    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.validation_issues)