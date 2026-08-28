from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., example="johndoe")
    email: str = Field(..., example="john@example.com")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
