from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import User, Mailbox
import uuid

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniMail API",
    description="Programmatic Mailbox Management System",
    version="1.0.0"
)

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

class MailboxResponse(BaseModel):
    id: str
    address: str
    is_active: bool

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
