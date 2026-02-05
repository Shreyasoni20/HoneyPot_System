from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import requests

from database import create_tables, get_db
from agent import generate_agent_reply
from intelligence import extract_intelligence, is_scam

API_KEY = "honeypot_api_key_2026"
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

app = FastAPI(title="Agentic Honeypot API")

# Create DB tables on startup
create_tables()

# -------------------- INPUT SCHEMAS --------------------

class Message(BaseModel):
    sender: str          # "scammer" or "user"
    text: str
    timestamp: str       # ISO-8601

class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Dict = {}

# -------------------- HEALTH --------------------

@app.get("/")
def health():
    return {"status": "Honeypot API is live"}

# -------------------- MAIN ENDPOINT --------------------

@app.post("/api/honeypot")
def honeypot_api(
    payload: HoneypotRequest,
    x_api_key: str = Header(...)
):
    # 1) API Key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    conn = get_db()
    cur = conn.cursor()

    # 2) Ensure session exists / update counters
    cur.execute(
        "INSERT OR IGNORE INTO sessions (session_id) VALUES (?)",
        (payload.sessionId,)
    )
    cur.execute(
        "UPDATE sessions SET total_messages = total_messages + 1 WHERE session_id = ?",
        (payload.sessionId,)
    )

    # 3) Store current message
    cur.execute(
        "INSERT INTO messages (session_id, sender, text, timestamp) VALUES (?, ?, ?, ?)",
        (
            payload.sessionId,
            payload.message.sender,
            payload.message.text,
            payload.message.timestamp
        )
    )

    # 4) Intelligence extraction
    intel = extract_intelligence(payload.message.text)
    scam = is_scam(intel)

    # 5) Agent reply (human-like, don’t reveal detection)
    reply = generate_agent_reply(payload.message.text)

    # 6) Final callback condition (as per GUVI rules)
    if scam and len(payload.conversationHistory) >= 2:
        # mark session as scam detected
        cur.execute(
            "UPDATE sessions SET scam_detected = 1 WHERE session_id = ?",
            (payload.sessionId,)
        )

        # store intelligence
        cur.execute("""
            INSERT INTO intelligence
            (session_id, bank_accounts, upids, phishing_links, phone_numbers, suspicious_keywords, agent_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.sessionId,
            ",".join(intel.get("bankAccounts", [])),
            ",".join(intel.get("upids", [])),
            ",".join(intel.get("phishingLinks", [])),
            ",".join(intel.get("phoneNumbers", [])),
            ",".join(intel.get("suspiciousKeywords", [])),
            "Scammer used urgency tactics and payment redirection"
        ))

        callback_payload = {
            "sessionId": payload.sessionId,
            "scamDetected": True,
            "totalMessagesExchanged": len(payload.conversationHistory) + 1,
            "extractedIntelligence": intel,
            "agentNotes": "Scammer used urgency tactics and payment redirection"
        }

        # send final result (mandatory)
        try:
            requests.post(CALLBACK_URL, json=callback_payload, timeout=5)
        except:
            pass  # never crash on callback failure

    conn.commit()
    conn.close()

    # 7) API response to platform
    return {
        "status": "success",
        "reply": reply
    }