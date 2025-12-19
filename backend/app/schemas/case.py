"""
Schemas Pydantic para gestión de casos
"""

from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date
from typing import Optional, Literal


class CaseOut(BaseModel):
    """Schema de salida para casos"""
    id: int
    student_id: int
    opened_at: date
    closed_at: Optional[date] = None
    status: Optional[Literal['INVESTIGATING', 'CONFIRMED', 'FALSE_ALARM', 'RESOLVED', 'MONITORING']] = None
    psychologist_notes: Optional[str] = None
    final_diagnosis: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CaseCreate(BaseModel):
    """Schema para crear un nuevo caso"""
    student_id: int
    opened_at: date
    closed_at: Optional[date] = None
    status: Optional[Literal['INVESTIGATING', 'CONFIRMED', 'FALSE_ALARM', 'RESOLVED', 'MONITORING']] = None
    psychologist_notes: Optional[str] = None
    final_diagnosis: Optional[str] = None

    @field_validator('status', 'psychologist_notes', 'final_diagnosis', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convierte cadenas vacías en None"""
        if isinstance(v, str) and v.strip() == '':
            return None
        return v


class CaseUpdate(BaseModel):
    """Schema para actualizar un caso"""
    status: Optional[Literal['INVESTIGATING', 'CONFIRMED', 'FALSE_ALARM', 'RESOLVED', 'MONITORING']] = None
    psychologist_notes: Optional[str] = None
    final_diagnosis: Optional[str] = None
    closed_at: Optional[date] = None

    @field_validator('status', 'psychologist_notes', 'final_diagnosis', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convierte cadenas vacías en None"""
        if isinstance(v, str) and v.strip() == '':
            return None
        return v
