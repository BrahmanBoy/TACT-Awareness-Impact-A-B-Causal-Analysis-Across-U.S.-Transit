from pydantic import BaseModel
from typing import List, Optional

class ABRequest(BaseModel):
    question_contains: str
    option: str = "yes"
    region: Optional[str] = None

class DIDRequest(BaseModel):
    question_contains: str
    option: str = "yes"
    treated_regions: List[str]
    control_regions: List[str]

class PSMRequest(BaseModel):
    question_contains: str
    option: str = "yes"
    features: List[str]
