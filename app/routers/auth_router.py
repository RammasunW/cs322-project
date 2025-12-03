from fastapi import APIRouter
from services.auth_service import register_user
from schemas.auth import RegisterRequest, RegisterResponse

router = APIRouter(prefix="/auth")

@router.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest):
    reg_id = register_user(req.username, req.email, req.password, req.phone)
    return RegisterResponse(registrationId=reg_id)
