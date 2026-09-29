from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class VaultEntryCreate(BaseModel):
    website: str
    username: str
    password: str = Field(min_length=1)
class VaultEntryUpdate(BaseModel):
    website: str
    username: str
    password: str = Field(min_length=1)