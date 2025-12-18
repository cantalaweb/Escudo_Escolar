"""
Schemas Pydantic para gestión de casos
"""

from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class CaseOut(BaseModel):
    """Schema de salida para casos"""
    id: int
    student_id: int
    opened_at: date
    closed_at: Optional[date] = None
    status: Optional[str] = None
    psychologist_notes: Optional[str] = None
    final_diagnosis: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CaseCreate(BaseModel):
    """Schema para crear un nuevo caso"""
    student_id: int
    opened_at: date
    closed_at: Optional[date] = None
    status: Optional[str] = None
    psychologist_notes: Optional[str] = None
    final_diagnosis: Optional[str] = None


class CaseUpdate(BaseModel):
    """Schema para actualizar un caso"""
    status: Optional[str] = None
    psychologist_notes: Optional[str] = None
    final_diagnosis: Optional[str] = None
    closed_at: Optional[date] = None
