"""
Schemas Pydantic para estudiantes
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class StudentBase(BaseModel):
    """Base para estudiante"""
    name: str
    class_id: int | None = None


class StudentCreate(StudentBase):
    """Schema para crear estudiante"""
    pass


class StudentOut(BaseModel):
    """Schema de salida para estudiante"""
    id: int
    name: str
    class_id: int | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StudentWithClass(StudentOut):
    """Schema de estudiante con información de clase"""
    class_name: str | None = None
