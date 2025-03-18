from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class NaturalLanguageQuery(BaseModel):
    query: str

class QueryResult(BaseModel):
    query: str
    sql: str
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None