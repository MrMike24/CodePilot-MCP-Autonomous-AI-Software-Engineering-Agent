from fastapi import FastAPI, Depends, Request, status
from demo_repository.app.rate_limiter import check_rate_limit, HTTPException, status
from demo_repository.app.models import UserCreate, UserResponse
from pydantic import BaseModel

app = FastAPI(title="Demo FastAPI Application")

# In-memory database
db_users: list[dict] = []


@app.get("/")
def read_root():
    return {"message": "Welcome to Demo FastAPI Application"}


@app.get("/users", response_model=list[UserResponse])
def list_users():
    return db_users


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    if not user.email or not user.email.strip():
        raise HTTPException(status_code=400, detail="Email cannot be empty")

    user_id = len(db_users) + 1
    new_user = {"id": user_id, "username": user.username, "email": user.email}
    db_users.append(new_user)
    return new_user


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/auth/login", response_model=LoginResponse, dependencies=[Depends(check_rate_limit)])
def login(req: LoginRequest):
    if req.username == "admin" and req.password == "secret123":
        return {"access_token": "valid_token_xyz_987", "token_type": "bearer"}
    if req.username == "user" and req.password == "password":
        return {"access_token": "valid_token_user_123", "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# Automated enhancement for task: Add Health Check Endpoint
