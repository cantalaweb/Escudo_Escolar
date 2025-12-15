"""
Endpoints de coordinación y análisis
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from typing import Optional

router = APIRouter(prefix="/coordinator", tags=["Coordinator"])


class SummaryTriggerRequest(BaseModel):
    """Request para generar resumen/análisis"""
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class SummaryResponse(BaseModel):
    """Response del trigger de análisis"""
    message: str
    job_id: str
    status: str = "initiated"


@router.post("/generate_summary", response_model=SummaryResponse)
def generate_summary(request: SummaryTriggerRequest):
    """
    Inicia el proceso de análisis y generación de resumen

    Args:
        request: Período de análisis (opcional)

    Returns:
        ID del job iniciado

    Note:
        Este endpoint dispara un proceso asíncrono que:
        1. Extrae features de todos los estudiantes
        2. Ejecuta el modelo de ML
        3. Genera alertas
        4. Notifica a los coordinadores
    """
    # TODO: Implementar lógica real de análisis
    # Por ahora retorna un mock

    return {
        "message": "Proceso de análisis iniciado correctamente",
        "job_id": "job_render_001",
        "status": "initiated"
    }
