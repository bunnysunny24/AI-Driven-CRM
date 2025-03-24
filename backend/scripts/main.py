from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from scripts.database import SessionLocal, Lead

app = FastAPI()

# Enable CORS (you can restrict origins if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for incoming lead data
class LeadIn(BaseModel):
    name: str
    email: str
    message: str
    source: str

# Endpoint to create a lead
@app.post("/leads")
def create_lead(lead: LeadIn):
    db = SessionLocal()
    try:
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
        return {"status": "Lead captured", "lead_id": new_lead.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving lead: {str(e)}")
    finally:
        db.close()
