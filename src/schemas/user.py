from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    password: str


class UserBase(BaseModel):
    id: int
    name: str
