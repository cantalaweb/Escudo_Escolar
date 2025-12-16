"""
Schemas Pydantic para autenticación
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Request para login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Información del usuario en la respuesta de login"""
    id: int
    name: str
    email: str
    role: str


class Token(BaseModel):
    """Response con el token JWT"""
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    """Datos decodificados del token"""
    user_id: int | None = None
