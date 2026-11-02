from fastapi import FastAPI, HTTPException, status
from typing import Dict

from backend.schemas import UserCreate, UserInDB
from backend.security import hash_password

app = FastAPI(title="User Registration API")

# In-memory "database" to store user data (for demonstration purposes)
# In a real application, this would be a proper database (e.g., PostgreSQL, MongoDB)
fake_users_db: Dict[str, UserInDB] = {}

@app.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """
    Registers a new user with a unique username and a bcrypt-hashed password.
    """
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )

    hashed_password = hash_password(user.password)
    user_in_db = UserInDB(username=user.username, hashed_password=hashed_password)
    fake_users_db[user.username] = user_in_db

    return user_in_db

@app.get("/")
async def read_root():
    return {"message": "Welcome to the User Registration API"}