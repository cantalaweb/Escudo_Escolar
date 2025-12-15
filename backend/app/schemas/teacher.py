"""
Schemas Pydantic para profesores
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class TeacherBase(BaseModel):
    """Base para profesor"""
    name: str
    email: EmailStr


class TeacherCreate(TeacherBase):
    """Schema para crear profesor"""
    password: str
    is_admin: bool = False


class TeacherOut(BaseModel):
    """Schema de salida para profesor"""
    id: int
    name: str
    email: EmailStr
    is_admin: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
