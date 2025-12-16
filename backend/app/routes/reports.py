"""
Endpoints para reportes de alumnos y profesores
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, datetime

from app.database.session import get_db
from app.models.database_models import (
    Class, Student, Teacher, TeacherClass,
    WitnessReport, TeacherReport
)
from app.schemas.common import ClassOut, MessageResponse
from app.schemas.student import StudentOut
from app.schemas.report import (
    WitnessReportCreate, WitnessReportOut,
    TeacherReportCreate, TeacherReportOut,
    StudentFeaturesOut
)
from app.core.security import get_current_user_id

router = APIRouter(prefix="/reports", tags=["Reports"])


# =============================================================================
# REPORTES DE ESTUDIANTES (TESTIGOS)
# =============================================================================

@router.get("/student/courses", response_model=List[ClassOut])
def get_courses_for_student_reports(db: Session = Depends(get_db)):
    """
    Obtiene todas las clases disponibles para reportes de estudiantes/testigos

    Returns:
        Lista de clases
    """
    classes = db.query(Class).all()
    return classes


@router.post("/student", response_model=MessageResponse)
def create_witness_report(
    report: WitnessReportCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un reporte de testigo anónimo

    Args:
        report: Datos del reporte (clase y fecha)
        db: Sesión de base de datos

    Returns:
        Mensaje de confirmación con ID del reporte
    """
    # Verificar que la clase existe
    class_exists = db.query(Class).filter(Class.id == report.class_id).first()
    if not class_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clase con ID {report.class_id} no encontrada"
        )

    db_report = WitnessReport(
        class_id=report.class_id,
        date=report.event_date or date.today()
    )

    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    return {
        "message": "Reporte de testigo registrado correctamente",
        "status": "success",
        "id": db_report.id
    }


# =============================================================================
# REPORTES DE PROFESORES
# =============================================================================

@router.get("/teacher/courses", response_model=List[ClassOut])
def get_courses_for_teacher(
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene las clases asignadas a un profesor autenticado

    Args:
        teacher_id: ID del profesor (extraído del token JWT)
        db: Sesión de base de datos

    Returns:
        Lista de clases asignadas al profesor
    """
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado"
        )

    # Obtener clases asignadas al profesor
    classes = (
        db.query(Class)
        .join(TeacherClass, TeacherClass.class_id == Class.id)
        .filter(TeacherClass.teacher_id == teacher_id)
        .all()
    )

    return classes


@router.get("/teacher/students/{class_id}", response_model=List[StudentOut])
def get_students_by_class(
    class_id: int,
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene los estudiantes de una clase específica

    Args:
        class_id: ID de la clase
        teacher_id: ID del profesor (extraído del token JWT)
        db: Sesión de base de datos

    Returns:
        Lista de estudiantes en la clase

    Raises:
        HTTPException: Si la clase no existe o el profesor no tiene acceso
    """
    # Verificar que la clase existe
    class_exists = db.query(Class).filter(Class.id == class_id).first()
    if not class_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clase con ID {class_id} no encontrada"
        )

    # Verificar que el profesor tiene acceso a esta clase
    has_access = (
        db.query(TeacherClass)
        .filter(
            TeacherClass.teacher_id == teacher_id,
            TeacherClass.class_id == class_id
        )
        .first()
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta clase"
        )

    students = db.query(Student).filter(Student.class_id == class_id).all()
    return students


@router.post("/teacher", response_model=MessageResponse)
def create_teacher_report(
    report: TeacherReportCreate,
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Crea un reporte de observación docente

    Args:
        report: Datos del reporte con métricas
        teacher_id: ID del profesor (extraído del token JWT)
        db: Sesión de base de datos

    Returns:
        Mensaje de confirmación
    """
    # Verificar que el estudiante existe
    student = db.query(Student).filter(Student.id == report.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {report.student_id} no encontrado"
        )

    new_report = TeacherReport(
        teacher_id=teacher_id,
        student_id=report.student_id,
        subject_id=report.subject_id,
        date=report.event_date or date.today(),
        disengagement=report.disengagement,
        social_isolation=report.social_isolation,
        peer_exclusion=report.peer_exclusion,
        emotional_reactivity=report.emotional_reactivity,
        inhibition=report.inhibition,
        physical_damage=report.physical_damage,
        intuition=report.intuition,
        notes=report.notes
    )

    db.add(new_report)
    db.commit()

    return {
        "message": "Reporte de profesor guardado correctamente",
        "status": "success"
    }


# =============================================================================
# EXTRACCIÓN DE FEATURES (Para ML)
# =============================================================================

@router.get("/features/{student_id}", response_model=StudentFeaturesOut)
def get_student_features(student_id: int, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas agregadas de un estudiante para el modelo ML

    Args:
        student_id: ID del estudiante
        db: Sesión de base de datos

    Returns:
        Features del estudiante (promedios y conteos)
    """
    try:
        stats = db.query(
            func.avg(TeacherReport.social_isolation).label('avg_isolation'),
            func.avg(TeacherReport.peer_exclusion).label('avg_exclusion'),
            func.avg(TeacherReport.emotional_reactivity).label('avg_emotion'),
            func.avg(TeacherReport.disengagement).label('avg_disengagement'),
            func.avg(TeacherReport.inhibition).label('avg_inhibition'),
            func.avg(TeacherReport.physical_damage).label('avg_physical'),
            func.avg(TeacherReport.intuition).label('avg_intuition'),
            func.count(TeacherReport.id).label('report_count')
        ).filter(TeacherReport.student_id == student_id).first()

        count = getattr(stats, 'report_count', 0) or 0

        return {
            "student_id": student_id,
            "features": {
                "avg_isolation": float(getattr(stats, 'avg_isolation', 0) or 0),
                "avg_exclusion": float(getattr(stats, 'avg_exclusion', 0) or 0),
                "avg_emotion": float(getattr(stats, 'avg_emotion', 0) or 0),
                "avg_disengagement": float(getattr(stats, 'avg_disengagement', 0) or 0),
                "avg_inhibition": float(getattr(stats, 'avg_inhibition', 0) or 0),
                "avg_physical": float(getattr(stats, 'avg_physical', 0) or 0),
                "avg_intuition": float(getattr(stats, 'avg_intuition', 0) or 0),
                "total_reports": int(count)
            },
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar features: {str(e)}"
        )
