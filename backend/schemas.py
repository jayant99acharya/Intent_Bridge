from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime

class IntentCreate(BaseModel):
    raw_text: str
    lat: float
    lng: float
    user_id: Optional[str] = "anonymous"

class IntentResponse(BaseModel):
    id: int
    user_id: str
    raw_text: str
    intent_type: str
    item_or_service: str
    urgency: str
    price_range: Optional[str] = None
    risk_score: float
    lat: float
    lng: float
    location_name: str
    safe_suggestions: Optional[str] = None
    action_plan: Optional[str] = None
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
