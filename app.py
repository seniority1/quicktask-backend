from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
from datetime import datetime

app = FastAPI(title="QuickTask.ng API")

# CORS (so frontend can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./quicktask.db"
engine = create_engine(DATABASE_URL, echo=True)

# User model
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    business_name: str
    email: str = Field(index=True, unique=True)
    phone: str = Field(index=True, unique=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(SQLModel):
    business_name: str
    email: str
    phone: str

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/users")
def create_user(payload: UserCreate):
    with Session(engine) as session:
        existing = session.exec(
            select(User).where((User.email == payload.email) | (User.phone == payload.phone))
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email or phone already registered")

        user = User(**payload.dict())
        session.add(user)
        session.commit()
        session.refresh(user)

        # TODO: send verification code via SMS/WhatsApp here

        return {"message": "User created. Verification pending.", "user_id": user.id}
