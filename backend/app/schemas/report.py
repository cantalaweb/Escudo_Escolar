"""
Schemas Pydantic para reportes
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional


class WitnessReportCreate(BaseModel):
    """Schema para crear reporte de testigo"""
    class_id: int = Field(..., gt=0, description="ID de la clase")
    event_date: Optional[date] = None


class WitnessReportOut(BaseModel):
    """Schema de salida para reporte de testigo"""
    id: int
    class_id: int
    date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeacherReportCreate(BaseModel):
    """Schema para crear reporte de profesor"""
    student_id: int = Field(..., gt=0, description="ID del estudiante")
    subject_id: Optional[int] = Field(None, gt=0, description="ID de la asignatura")

    # Métricas (Escala Likert 0-3)
    academic_performance: int = Field(..., ge=0, le=3, description="Rendimiento académico")
    social_isolation: int = Field(..., ge=0, le=3, description="Aislamiento social")
    peer_exclusion: int = Field(..., ge=0, le=3, description="Exclusión por compañeros")
    emotional_reactivity: int = Field(..., ge=0, le=3, description="Reactividad emocional")
    inhibition: int = Field(..., ge=0, le=3, description="Inhibición")
    physical_damage: int = Field(..., ge=0, le=3, description="Daño físico observable")
    intuition: int = Field(..., ge=0, le=3, description="Intuición del profesor")

    notes: Optional[str] = Field(None, max_length=2000, description="Notas adicionales")
    event_date: Optional[date] = None


class TeacherReportOut(BaseModel):
    """Schema de salida para reporte de profesor"""
    id: int
    teacher_id: int | None
    student_id: int | None
    subject_id: int | None
    date: date
    academic_performance: int
    social_isolation: int
    peer_exclusion: int
    emotional_reactivity: int
    inhibition: int
    physical_damage: int
    intuition: int
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentFeaturesOut(BaseModel):
    """Schema para features de estudiante (usado por ML)"""
    student_id: int
    features: dict
    timestamp: datetime
