<<<<<<< HEAD
from pydantic import BaseModel, EmailStr
from typing import Optional
=======
from pydantic import BaseModel
>>>>>>> da9a447 (git feat:(User Model and CRUD): Start adding Files)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None

class UserRead(BaseModel):
    id: int
    username: str
    email: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):    #Separate from above for secure password handling 
    current_password: str
    new_password: str
    class Config:
        orm_mode = True
