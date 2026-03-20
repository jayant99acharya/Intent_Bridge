import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine, SessionLocal
import models

# Setup test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "IntentBridge API is running"}

def test_create_intent_integration():
    # This tests the endpoint which calls Gemini. 
    # Since we can't reliably call Gemini in a unit test, we check if it returns a valid response structure
    payload = {
        "raw_text": "I want to sell my old cycle for 2000 rupees near Bandra",
        "lat": 19.0596,
        "lng": 72.8295,
        "user_id": "test_user"
    }
    response = client.post("/api/intent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user"
    assert "id" in data
    assert "intent_type" in data
    assert "item_or_service" in data

def test_get_intents():
    response = client.get("/api/intents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_database_persistence(db):
    new_intent = models.Intent(
        raw_text="Test persistence",
        intent_type="test",
        item_or_service="test_item",
        urgency="low",
        lat=0.0,
        lng=0.0,
        location_name="Test Loc",
        risk_score=1.0
    )
    db.add(new_intent)
    db.commit()
    db.refresh(new_intent)
    
    assert new_intent.id is not None
    assert new_intent.raw_text == "Test persistence"
