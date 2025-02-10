from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id : Optional[str]  = None
    username: str
    full_name: Optional[str] = None 
    email: str
    password: str


