from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app import models
from app.security import hash_password, verify_password
from fastapi import FastAPI, Depends, HTTPException 
from app.schemas import UserCreate, UserLogin

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SecureVault API",
    description="Backend API for the SecureVault password manager",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Welcome to SecureVault"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@app.post("/api/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    

    return {
        "message": "User registered successfully",
        "id": new_user.id,
        "email": new_user.email
    }
@app.post("/api/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "id": db_user.id,
        "email": db_user.email
    }