from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import register_user, authenticate_user

router = APIRouter()

class RegisterInput(BaseModel):
    username: str
    email: str
    password: str

class LoginInput(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(data: RegisterInput):
    try:
        user_id = register_user(data.username, data.email, data.password)
        return {"message": "User registered successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Registration failed. Username or email may already exist.")

@router.post("/login")
def login(data: LoginInput):
    try:
        user_id = authenticate_user(data.username, data.password)
        if user_id:
            return {"message":  "Login Successfull", "user_id": user_id}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Login error")
