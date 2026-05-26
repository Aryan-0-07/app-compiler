import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from schemas.db_schema import DBSchema
from schemas.api_schema import APISchema

TYPE_MAP = {
    "string": "TEXT",
    "str": "TEXT",
    "integer": "INTEGER",
    "int": "INTEGER",
    "float": "REAL",
    "boolean": "INTEGER",
    "bool": "INTEGER",
    "datetime": "TEXT",
    "date": "TEXT",
    "text": "TEXT",
    "uuid": "TEXT",
}

def db_schema_to_sql(db_schema: DBSchema) -> list:
    statements = []
    for table in db_schema.tables:
        cols = []
        for col in table.columns:
            sql_type = TYPE_MAP.get(col.type.lower(), "TEXT")
            parts = [f"{col.name} {sql_type}"]
            if col.primary_key:
                parts.append("PRIMARY KEY")
            if not col.nullable and not col.primary_key:
                parts.append("NOT NULL")
            if col.unique:
                parts.append("UNIQUE")
            if col.default:
                parts.append(f"DEFAULT '{col.default}'")
            cols.append(" ".join(parts))
        stmt = f"CREATE TABLE IF NOT EXISTS {table.name} ({', '.join(cols)});"
        statements.append(stmt)
    return statements


def execute_db_schema(db_schema: DBSchema) -> dict:
    result = {
        "success": False,
        "tables_created": [],
        "errors": [],
        "sql_statements": []
    }
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        statements = db_schema_to_sql(db_schema)
        result["sql_statements"] = statements
        for stmt in statements:
            try:
                cursor.execute(stmt)
                table_name = stmt.split("IF NOT EXISTS ")[1].split(" ")[0]
                result["tables_created"].append(table_name)
            except Exception as e:
                result["errors"].append(f"SQL error: {str(e)} | Statement: {stmt}")
        conn.commit()
        conn.close()
        result["success"] = len(result["errors"]) == 0
    except Exception as e:
        result["errors"].append(f"DB execution failed: {str(e)}")
    return result


def validate_api_schema(api_schema: APISchema) -> dict:
    result = {
        "success": False,
        "endpoints_validated": [],
        "errors": []
    }
    try:
        for endpoint in api_schema.endpoints:
            issues = []
            if not endpoint.path.startswith("/"):
                issues.append(f"Path must start with /: {endpoint.path}")
            if not endpoint.name:
                issues.append("Endpoint missing name")
            if not endpoint.response_fields:
                issues.append(f"Endpoint {endpoint.name} has no response fields")
            if issues:
                result["errors"].extend(issues)
            else:
                result["endpoints_validated"].append(endpoint.path)
        result["success"] = len(result["errors"]) == 0
    except Exception as e:
        result["errors"].append(f"API validation failed: {str(e)}")
    return result


def run_runtime_checks(bundle) -> dict:
    print("\n" + "=" * 50)
    print("Runtime Execution Check")
    print("=" * 50)

    db_result = execute_db_schema(bundle.db)
    print(f"DB Execution: {'✅ passed' if db_result['success'] else '❌ failed'}")
    if db_result["tables_created"]:
        print(f"  Tables created: {', '.join(db_result['tables_created'])}")
    if db_result["errors"]:
        for err in db_result["errors"]:
            print(f"  Error: {err}")

    api_result = validate_api_schema(bundle.api)
    print(f"API Validation: {'✅ passed' if api_result['success'] else '❌ failed'}")
    if api_result["endpoints_validated"]:
        print(f"  Endpoints validated: {len(api_result['endpoints_validated'])}")
    if api_result["errors"]:
        for err in api_result["errors"]:
            print(f"  Error: {err}")

    overall_success = db_result["success"] and api_result["success"]
    print(f"\nOverall Runtime: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    print("=" * 50)

    return {
        "success": overall_success,
        "db": db_result,
        "api": api_result
    }