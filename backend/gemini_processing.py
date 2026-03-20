from google import genai as google_genai
import os
import json
import logging

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCRdsd7zmxHCFG-pbpejywTIAHw2bK-7b4")
_client = google_genai.Client(api_key=GEMINI_API_KEY)
MODELS_TO_TRY = ["models/gemini-2.0-flash-lite", "models/gemini-2.5-flash", "models/gemini-2.0-flash"]

import datetime

def extract_intent_from_text(raw_text: str, lat: float, lng: float, image_data: bytes = None):
    """
    Uses Gemini API to structure the unstructured text with Situation Awareness.
    """
    # Situation-Aware Context (In real app, we'd fetch actual weather/news)
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    mock_weather = "Rainy" if "rain" in raw_text.lower() else "Clear"
    
    context_prompt = f"""
    Context:
    - Current Time: {current_time}
    - Weather: {mock_weather}
    - User Coordinates: ({lat}, {lng})
    """
    
    prompt = f"""
    You are an AI processing unstructured human intent for IntentBridge.
    {context_prompt}
    
    User Input: "{raw_text}"
    
    Analyze and extract:
    - intent_type (buy, sell, meet, trade)
    - item_or_service
    - location_inferred
    - urgency (high, medium, low)
    - suggested_price_range
    - risk_score (0.0 to 1.0, 1.0 is safest)
    - safe_meetup_suggestions (List of 2-3 specific safe, public spots near the location)
    - action_plan (1-2 steps for the user)

    Respond with ONLY raw JSON.
    """
    
    try:
        last_error = None
        response = None
        
        # Prepare content list for multimodal support
        contents = [prompt]
        if image_data:
            contents.append({"mime_type": "image/jpeg", "data": image_data})
            
        for model_name in MODELS_TO_TRY:
            try:
                response = _client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
                break
            except Exception as model_err:
                logger.warning(f"Model {model_name} failed: {model_err}")
                last_error = model_err
        
        if response is None:
            raise last_error
            
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:-3].strip()
        elif text_response.startswith("```"):
            text_response = text_response[3:-3].strip()
            
        structured_data = json.loads(text_response)
        return structured_data
    except Exception as e:
        logger.error(f"Error in Gemini Processing: {e}")
        return {
            "intent_type": "unknown",
            "item_or_service": "unknown",
            "location_inferred": "Current Location",
            "urgency": "medium",
            "suggested_price_range": "Negotiable",
            "risk_score": 0.5,
            "safe_meetup_suggestions": ["Nearby Police Station", "Public Square"],
            "action_plan": ["Wait for verified matches"]
        }

