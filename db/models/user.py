from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id : str | None = None
    username: str
    email: str

