from sqlalchemy import Column, Integer, String, Float, DateTime
import datetime
from database import Base

class Intent(Base):
    __tablename__ = "intents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, default="anonymous")
    raw_text = Column(String, index=True)
    intent_type = Column(String, index=True) # buy, sell, meet
    item_or_service = Column(String, index=True)
    urgency = Column(String)
    price_range = Column(String)
    risk_score = Column(Float)
    lat = Column(Float)
    lng = Column(Float)
    location_name = Column(String)
    safe_suggestions = Column(String) # JSON string of suggestions
    action_plan = Column(String) # JSON string of steps
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
