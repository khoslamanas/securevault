from fastapi import FastAPI

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