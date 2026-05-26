from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel, field_validator

class DBColumn(BaseModel):
    name: str
    type: str
    primary_key: bool = False
    nullable: bool = False
    default: Optional[str] = None

    @field_validator('default', mode='before')
    @classmethod
    def coerce_default_to_str(cls, v):
        if v is None:
            return None
        if isinstance(v, bool):
            return None
        return str(v)
    foreign_key: Optional[str] = None
    unique: bool = False

class DBTable(BaseModel):
    name: str
    columns: List[DBColumn]
    indexes: List[str] = []

class DBSchema(BaseModel):
    tables: List[DBTable]

    def get_table(self, name: str) -> Optional[DBTable]:
        return next((t for t in self.tables if t.name == name), None)

    def get_column_names(self, table_name: str) -> List[str]:
        table = self.get_table(table_name)
        return [c.name for c in table.columns] if table else []