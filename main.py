from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid

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
    address: str  # e.g., "hello@omnimail.com"

class MailboxResponse(BaseModel):
    id: str
    address: str
    is_active: bool

# --- Security ---

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    # Logic to validate against DB will go here
    if api_key == "test_secret_key":
        return api_key
    raise HTTPException(status_code=403, detail="Invalid API Key")

# --- Routes ---

@app.get("/health")
def health_check():
    return {"status": "ok", "engine": "OmniMail"}

@app.post("/register", response_model=UserResponse, tags=["Auth"])
def register_user(user: UserCreate):
    """
    Registers a new developer and generates an API Key.
    """
    new_api_key = f"omni_{uuid.uuid4().hex}"
    return {
        "id": str(uuid.uuid4()),
        "api_key": new_api_key,
        "org_name": user.org_name
    }

@app.post("/mailboxes", response_model=MailboxResponse, tags=["Mailboxes"])
def create_mailbox(mailbox: MailboxCreate, api_key: str = Depends(get_api_key)):
    """
    Creates a new programmatic mailbox.
    """
    return {
        "id": str(uuid.uuid4()),
        "address": mailbox.address,
        "is_active": True
    }

@app.get("/mailboxes", response_model=List[MailboxResponse], tags=["Mailboxes"])
def list_mailboxes(api_key: str = Depends(get_api_key)):
    """
    Lists all mailboxes associated with the current API key.
    """
    return [
        {"id": "mb_123", "address": "test@omnimail.com", "is_active": True}
    ]
