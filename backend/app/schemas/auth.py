"""
Schemas Pydantic para autenticación
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Request para login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Response con el token JWT"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Datos decodificados del token"""
    user_id: int | None = None
