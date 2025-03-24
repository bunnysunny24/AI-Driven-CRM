from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database import SessionLocal, Lead

app = FastAPI()

class LeadIn(BaseModel):
    name: str
    email: str
    message: str
    source: str

@app.post("/leads")
def create_lead(lead: LeadIn):
    db = SessionLocal()
    new_lead = Lead(
        name=lead.name,
        email=lead.email,
        message=lead.message,
        source=lead.source,
        timestamp=datetime.utcnow()
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    db.close()
    return {"status": "Lead captured", "lead_id": new_lead.id}
