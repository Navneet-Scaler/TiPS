from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OpportunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    summary: Optional[str] = None
    url: str
    category: str
    subcategory: Optional[str] = None
    organization: Optional[str] = None
    geography: str
    is_remote: bool
    is_paid: bool
    deadline: Optional[datetime] = None
    is_rolling: bool = False
    dilution_type: Optional[str] = None
    published_at: Optional[datetime] = None
    discovered_at: datetime
    score: float


class StatsOut(BaseModel):
    total: int
    new_today: int
    new_this_week: int
    by_category: dict
    by_organization: dict
