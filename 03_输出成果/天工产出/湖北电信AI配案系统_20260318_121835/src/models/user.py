"""用户模型"""
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
