"""
Schemas Pydantic comunes y reutilizables
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime, date


class ClassOut(BaseModel):
    """Schema de salida para clases/aulas"""
    id: int
    name: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SubjectOut(BaseModel):
    """Schema de salida para asignaturas"""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Response genérico con mensaje"""
    message: str
    status: str = "success"
    id: int | None = None
