from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app import models
from app.security import hash_password, verify_password, create_access_token, decode_access_token, encrypt_password, decrypt_password
from fastapi import FastAPI, Depends, HTTPException 
from app.schemas import UserCreate, UserLogin, VaultEntryCreate, VaultEntryUpdate
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import string
app = FastAPI(
    title="SecureVault API",
    description="Backend API for the SecureVault password manager",
    version="1.0.0"
)
security = HTTPBearer()

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

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload

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

    access_token = create_access_token(
        data={"sub": str(db_user.id), "email": db_user.email}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }
@app.get("/api/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["sub"],
        "email": current_user["email"]
    }
@app.post("/api/vault")
def create_vault_entry(
    entry: VaultEntryCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    encrypted = encrypt_password(entry.password)

    new_entry = models.VaultEntry(
        user_id=int(current_user["sub"]),
        website=entry.website,
        username=entry.username,
        encrypted_password=encrypted
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return {
        "message": "Password saved successfully",
        "id": new_entry.id,
        "website": new_entry.website,
        "username": new_entry.username
    }
@app.get("/api/vault")
def get_vault_entries(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entries = db.query(models.VaultEntry).filter(
        models.VaultEntry.user_id == int(current_user["sub"])
    ).all()

    return [
        {
            "id": entry.id,
            "website": entry.website,
            "username": entry.username,
            "password": decrypt_password(entry.encrypted_password)
        }
        for entry in entries
    ]
@app.delete("/api/vault/{entry_id}")
def delete_vault_entry(
    entry_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(models.VaultEntry).filter(
        models.VaultEntry.id == entry_id,
        models.VaultEntry.user_id == int(current_user["sub"])
    ).first()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Vault entry not found"
        )

    db.delete(entry)
    db.commit()

    return {
        "message": "Password deleted successfully"
    }
@app.put("/api/vault/{entry_id}")
def update_vault_entry(
    entry_id: int,
    updated_entry: VaultEntryUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(models.VaultEntry).filter(
        models.VaultEntry.id == entry_id,
        models.VaultEntry.user_id == int(current_user["sub"])
    ).first()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Vault entry not found"
        )

    entry.website = updated_entry.website
    entry.username = updated_entry.username
    entry.encrypted_password = encrypt_password(updated_entry.password)

    db.commit()
    db.refresh(entry)

    return {
        "message": "Password updated successfully",
        "id": entry.id,
        "website": entry.website,
        "username": entry.username
    }
@app.get("/api/generate-password")
def generate_password(length: int = 16):
    if length < 12 or length > 128:
        raise HTTPException(
            status_code=400,
            detail="Password length must be between 12 and 128"
        )

    characters = string.ascii_letters + string.digits + "!@#$%^&*"

    while True:
        password = "".join(
            secrets.choice(characters)
            for _ in range(length)
        )

        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            break

    return {"password": password}