import re

def extract_intelligence(text: str):
    return {
        "bankAccounts": re.findall(r"\b\d{4}-\d{4}-\d{4}\b", text),
        "upids": re.findall(r"\b[\w.-]+@upi\b", text),
        "phishingLinks": re.findall(r"https?://\S+", text),
        "phoneNumbers": re.findall(r"\b\d{10}\b", text),
        "suspiciousKeywords": [
            k for k in ["urgent", "verify", "blocked", "suspend"]
            if k in text.lower()
        ]
    }

def is_scam(intel: dict):
    return len(intel["suspiciousKeywords"]) > 0