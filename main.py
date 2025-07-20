from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import User, Mailbox, EmailMessage
from app.services.smtp_handler import start_smtp_server
import uuid
import asyncio

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniMail API",
    description="Programmatic Mailbox Management System",
    version="1.0.0"
)

# Start SMTP server in the background on startup
@app.on_event("startup")
async def startup_event():
    # Run in a separate thread/task so it doesn't block FastAPI
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, start_smtp_server, "0.0.0.0", 25) # Default SMTP port

# --- Schemas ---

class UserCreate(BaseModel):
    email: EmailStr
    org_name: str

class UserResponse(BaseModel):
    id: str
    api_key: str
    org_name: str

class MailboxCreate(BaseModel):
    address: str
    webhook_url: Optional[str] = None

class MailboxResponse(BaseModel):
    id: str
    address: str
    webhook_url: Optional[str]
    is_active: bool

class EmailResponse(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    received_at: datetime

# --- Security ---

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_current_user(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return user

# --- Routes ---

@app.get("/health")
def health_check():
    return {"status": "ok", "engine": "OmniMail"}

@app.post("/register", response_model=UserResponse, tags=["Auth"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new developer and generates an API Key.
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return existing_user
        
    db_user = User(
        email=user.email,
        org_name=user.org_name,
        api_key=f"omni_{uuid.uuid4().hex}"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/mailboxes", response_model=MailboxResponse, tags=["Mailboxes"])
def create_mailbox(
    mailbox_in: MailboxCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new programmatic mailbox.
    """
    db_mailbox = Mailbox(
        address=mailbox_in.address,
        webhook_url=mailbox_in.webhook_url,
        user_id=current_user.id
    )
    db.add(db_mailbox)
    db.commit()
    db.refresh(db_mailbox)
    return db_mailbox

@app.get("/mailboxes", response_model=List[MailboxResponse], tags=["Mailboxes"])
def list_mailboxes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists all mailboxes associated with the current API key.
    """
    return db.query(Mailbox).filter(Mailbox.user_id == current_user.id).all()

@app.get("/mailboxes/{mailbox_id}/messages", response_model=List[EmailResponse], tags=["Emails"])
def list_messages(
    mailbox_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists all incoming emails for a specific mailbox.
    """
    # Security check: ensure mailbox belongs to user
    mailbox = db.query(Mailbox).filter(Mailbox.id == mailbox_id, Mailbox.user_id == current_user.id).first()
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    
    return db.query(EmailMessage).filter(EmailMessage.mailbox_id == mailbox_id).all()
