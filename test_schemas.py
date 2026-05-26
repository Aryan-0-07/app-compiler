from schemas import (
    IntentOutput, ArchOutput,
    UISchema, APISchema, DBSchema, AuthSchema,
    SchemaBundle, ValidationIssue
)

print("All schema contracts loaded successfully.")
print(f"IntentOutput fields: {list(IntentOutput.model_fields.keys())}")
print(f"SchemaBundle fields: {list(SchemaBundle.model_fields.keys())}")