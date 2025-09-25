from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Category(BaseModel):
    id: str
    label: str
    weight: float = 1.0

class Weighting(BaseModel):
    teacherPct: int = 50
    peersPct: int = 50

class Session(BaseModel):
    id: str
    classId: str
    title: str
    description: Optional[str] = ""
    tags: List[str] = []
    categories: List[Category] = []
    weighting: Weighting = Field(default_factory=Weighting)
    status: str = "scheduled"  # scheduled|open|closed|archived
    allowEditsUntilClose: bool = True
    graceMinutes: int = 0
    createdAt: Optional[datetime] = None
    openedAt: Optional[datetime] = None
    closedAt: Optional[datetime] = None

class Vote(BaseModel):
    userId: str
    teamId: str
    ratings: Dict[str, int]  # {categoryId: 1..5}
    superVote: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
