from pydantic import BaseModel
from typing import List, Optional

class GraphMLResult(BaseModel):
    graphml: str

class ParseTaskStatus(BaseModel):
    status: str
    progress: int
    result: Optional[str] = None