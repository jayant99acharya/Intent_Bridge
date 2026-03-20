import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import axios from 'axios';
import { Sparkles, MapPin, Navigation, Send, ShieldCheck, AlertTriangle } from 'lucide-react';

// Fix for default marker icons in React Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const API_URL = 'http://localhost:8000/api';

// Create custom colored icons based on intent type
const getCustomIcon = (type) => {
  const colorMap = {
    sell: '#3b82f6', // blue
    buy: '#10b981',  // green
    meet: '#8b5cf6', // purple
    trade: '#f59e0b',// orange
  };
  const color = colorMap[type] || '#ef4444';
  
  const markerHtmlStyles = `
    background-color: ${color};
    width: 2rem;
    height: 2rem;
    display: block;
    left: -1rem;
    top: -1rem;
    position: relative;
    border-radius: 3rem 3rem 0;
    transform: rotate(45deg);
    border: 2px solid #FFFFFF;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  `;

  return L.divIcon({
    className: "my-custom-pin",
    iconAnchor: [0, 24],
    labelAnchor: [-6, 0],
    popupAnchor: [0, -36],
    html: `<span style="${markerHtmlStyles}" />`
  });
}


function App() {
  const [intents, setIntents] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  
  // Default bounds / location (e.g. Bandra/Mumbai)
  const defaultCenter = [19.0596, 72.8295];
  const [currentLoc, setCurrentLoc] = useState(defaultCenter);

  useEffect(() => {
    fetchIntents();
    // Try to get actual location
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setCurrentLoc([pos.coords.latitude, pos.coords.longitude]),
        (err) => console.log(err)
      );
    }
  }, []);

  const fetchIntents = async () => {
    try {
      const res = await axios.get(`${API_URL}/intents`);
      setIntents(res.data);
    } catch (e) {
      console.error("Failed to fetch intents", e);
    }
  };

  const handleSubmitIntent = async () => {
    if (!inputText.trim()) return;
    setIsSynthesizing(true);
    try {
      const response = await axios.post(`${API_URL}/intent`, {
        raw_text: inputText,
        lat: currentLoc[0],
        lng: currentLoc[1]
      });
      setIntents([...intents, response.data]);
      setInputText("");
    } catch (e) {
      console.error("Submit failed", e);
      alert("Failed to structure intent via Gemini. Is the backend running?");
    } finally {
      setIsSynthesizing(false);
    }
  };

  return (
    <div className="app-container">
      <div className="map-container">
        <MapContainer center={currentLoc} zoom={13} zoomControl={false}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />
          {intents.map((intent) => (
            <Marker 
              key={intent.id} 
              position={[intent.lat, intent.lng]}
              icon={getCustomIcon(intent.intent_type)}
            >
              <Popup className="custom-popup">
                <div className="intent-popup">
                  <h3>
                    <span>{intent.item_or_service}</span>
                    <span className={`badge ${intent.intent_type}`}>{intent.intent_type}</span>
                  </h3>
                  <p><strong>Urgency:</strong> {intent.urgency}</p>
                  <p><strong>Original Intent:</strong> "{intent.raw_text}"</p>
                  
                  {intent.safe_suggestions && (
                    <div className="ai-suggestions">
                      <strong>🛡️ Safe Meetups:</strong>
                      <ul>
                        {JSON.parse(intent.safe_suggestions).map((s, i) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                  )}

                  {intent.action_plan && (
                    <div className="ai-plan">
                      <strong>📝 AI Action Plan:</strong>
                      <p>{JSON.parse(intent.action_plan).join(" → ")}</p>
                    </div>
                  )}

                  <div className="risk-score">
                    {intent.risk_score >= 0.7 ? (
                       <><ShieldCheck size={16} className="safe" /> <span className="safe">Verified Safe ({intent.risk_score})</span></>
                    ) : (
                       <><AlertTriangle size={16} className="risky" /> <span className="risky">Caution ({intent.risk_score})</span></>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      <div className="ui-overlay">
        <div className="header" role="banner">
          <h1 aria-label="IntentBridge: AI Geo-Intent Marketplace">
            <Sparkles size={24} color="#8b5cf6" aria-hidden="true" /> IntentBridge
          </h1>
          <div className="hint-text" aria-live="polite">
            <Navigation size={16} aria-hidden="true" /> Live Map: Situation Aware
          </div>
        </div>

        <div className="intent-panel" role="form" aria-label="Submit your intent">
          <div className="intent-input-wrapper">
            <textarea 
              className="intent-textarea"
              placeholder="What do you want to do? (e.g., 'Selling hot chai, safe meetups only')"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isSynthesizing}
              aria-label="Your intent description"
            />
            <div className="intent-controls">
              <span className="hint-text">
                <MapPin size={16} aria-hidden="true" /> Situation-aware synthesis active
              </span>
              <button 
                className="submit-btn" 
                onClick={handleSubmitIntent}
                disabled={isSynthesizing || !inputText.trim()}
                aria-busy={isSynthesizing}
              >
                {isSynthesizing ? (
                  <><div className="loader"></div> Processing...</>
                ) : (
                  <>Synthesize & Verify <Send size={18} aria-hidden="true" /></>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
