from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    phone: str

class RegisterResponse(BaseModel):
    registrationId: int | str
