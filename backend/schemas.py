from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    """Schema for user registration request."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserInDB(BaseModel):
    """Schema for user data stored in the database."""
    username: str
    hashed_password: str