import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from schemas.bundle import SchemaBundle, ValidationIssue


def validate_db_api_consistency(bundle: SchemaBundle) -> list[ValidationIssue]:
    """Check that every API endpoint's db_table exists in DB schema"""
    issues = []
    db_table_names = [t.name for t in bundle.db.tables]

    for endpoint in bundle.api.endpoints:
        if endpoint.db_table and endpoint.db_table not in db_table_names:
            issues.append(ValidationIssue(
                layer="api",
                severity="error",
                message=f"Endpoint '{endpoint.name}' references db_table '{endpoint.db_table}' which does not exist in DB schema",
                field=endpoint.db_table
            ))

        for field in endpoint.response_fields:
            if field.maps_to_db_column and endpoint.db_table:
                table = bundle.db.get_table(endpoint.db_table)
                if table:
                    col_names = [c.name for c in table.columns]
                    if field.maps_to_db_column not in col_names:
                        issues.append(ValidationIssue(
                            layer="api",
                            severity="error",
                            message=f"Endpoint '{endpoint.name}' response field '{field.name}' maps to column '{field.maps_to_db_column}' which does not exist in table '{endpoint.db_table}'",
                            field=field.maps_to_db_column
                        ))

    return issues


def validate_ui_api_consistency(bundle: SchemaBundle) -> list[ValidationIssue]:
    """Check that every UI page's api_calls reference real endpoints"""
    issues = []
    endpoint_names = [e.name for e in bundle.api.endpoints]

    for page in bundle.ui.pages:
        for api_call in page.api_calls:
            if api_call not in endpoint_names:
                issues.append(ValidationIssue(
                    layer="ui",
                    severity="error",
                    message=f"Page '{page.name}' calls API '{api_call}' which does not exist in API schema",
                    field=api_call
                ))

    return issues


def validate_auth_roles_consistency(bundle: SchemaBundle) -> list[ValidationIssue]:
    """Check that all roles referenced in UI and API exist in Auth schema"""
    issues = []
    auth_roles = bundle.auth.get_role_names()

    for endpoint in bundle.api.endpoints:
        for role in endpoint.allowed_roles:
            if role not in auth_roles:
                issues.append(ValidationIssue(
                    layer="api",
                    severity="error",
                    message=f"Endpoint '{endpoint.name}' allows role '{role}' which does not exist in Auth schema",
                    field=role
                ))

    for page in bundle.ui.pages:
        for role in page.allowed_roles:
            if role not in auth_roles:
                issues.append(ValidationIssue(
                    layer="ui",
                    severity="error",
                    message=f"Page '{page.name}' allows role '{role}' which does not exist in Auth schema",
                    field=role
                ))

    return issues


def validate_db_required_columns(bundle: SchemaBundle) -> list[ValidationIssue]:
    """Check that every table has id, created_at, updated_at"""
    issues = []
    required_columns = ["id", "created_at", "updated_at"]

    for table in bundle.db.tables:
        col_names = [c.name for c in table.columns]
        for required in required_columns:
            if required not in col_names:
                issues.append(ValidationIssue(
                    layer="db",
                    severity="error",
                    message=f"Table '{table.name}' is missing required column '{required}'",
                    field=required
                ))

    return issues


def validate_foreign_keys(bundle: SchemaBundle) -> list[ValidationIssue]:
    """Check that all foreign keys reference real tables"""
    issues = []
    db_table_names = [t.name for t in bundle.db.tables]

    for table in bundle.db.tables:
        for column in table.columns:
            if column.foreign_key:
                ref_table = column.foreign_key.split(".")[0]
                if ref_table not in db_table_names:
                    issues.append(ValidationIssue(
                        layer="db",
                        severity="error",
                        message=f"Column '{table.name}.{column.name}' has foreign key '{column.foreign_key}' referencing non-existent table '{ref_table}'",
                        field=column.foreign_key
                    ))

    return issues


def run_all_validations(bundle: SchemaBundle) -> SchemaBundle:
    """Run all validation checks and return bundle with issues populated"""
    print("\nRunning cross-layer validations...")
    all_issues = []

    checks = [
        ("DB ↔ API consistency", validate_db_api_consistency),
        ("UI ↔ API consistency", validate_ui_api_consistency),
        ("Auth roles consistency", validate_auth_roles_consistency),
        ("DB required columns", validate_db_required_columns),
        ("Foreign key references", validate_foreign_keys),
    ]

    for check_name, check_fn in checks:
        issues = check_fn(bundle)
        if issues:
            print(f"  ❌ {check_name}: {len(issues)} issue(s) found")
            all_issues.extend(issues)
        else:
            print(f"  ✅ {check_name}: passed")

    bundle.validation_issues = all_issues
    bundle.is_valid = len([i for i in all_issues if i.severity == "error"]) == 0

    return bundle