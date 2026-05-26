import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from schemas.intent import IntentOutput, Entity, Feature, ClarificationRequest
from schemas.architecture import ArchOutput, Relation, RolePermission
from schemas.ui_schema import UISchema, UIPage, UIField
from schemas.api_schema import APISchema, APIEndpoint, APIField
from schemas.db_schema import DBSchema, DBTable, DBColumn
from schemas.auth_schema import AuthSchema, Role, Permission
from schemas.bundle import SchemaBundle, ValidationIssue

print("All schema contracts loaded successfully.")
print(f"IntentOutput fields: {list(IntentOutput.model_fields.keys())}")
print(f"SchemaBundle fields: {list(SchemaBundle.model_fields.keys())}")