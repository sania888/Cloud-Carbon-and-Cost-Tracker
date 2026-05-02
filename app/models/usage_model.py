from pydantic import BaseModel
from typing import List


class UsageSchema(BaseModel):
    service: str
    region: str
    usage_hours: float
    usage_type: str
    cost_usd: float
    emission_kg: float
    

REQUIRED_COLUMS = [
    "service",
    "region",
    "usage_hours",
    "usage_type",
    "cost_usd",
    "emission_kg"
]