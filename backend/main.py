from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

import models, schemas, database, gemini_processing

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="IntentBridge API")

# Setup CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "IntentBridge API is running"}

import json

@app.post("/api/intent", response_model=schemas.IntentResponse)
def create_intent(intent: schemas.IntentCreate, db: Session = Depends(database.get_db)):
    # 1. Process with Gemini
    structured = gemini_processing.extract_intent_from_text(
        intent.raw_text, intent.lat, intent.lng
    )
    
    # 2. Save to DB
    db_intent = models.Intent(
        user_id=intent.user_id,
        raw_text=intent.raw_text,
        intent_type=structured.get("intent_type", "unknown"),
        item_or_service=structured.get("item_or_service", "unknown"),
        urgency=structured.get("urgency", "medium"),
        price_range=structured.get("suggested_price_range", "Negotiable"),
        risk_score=structured.get("risk_score", 0.5),
        lat=intent.lat,
        lng=intent.lng,
        location_name=structured.get("location_inferred", "Current Location"),
        safe_suggestions=json.dumps(structured.get("safe_meetup_suggestions", [])),
        action_plan=json.dumps(structured.get("action_plan", []))
    )
    db.add(db_intent)
    db.commit()
    db.refresh(db_intent)
    
    return db_intent

@app.get("/api/intents", response_model=List[schemas.IntentResponse])
def get_intents(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    intents = db.query(models.Intent).offset(skip).limit(limit).all()
    return intents

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
