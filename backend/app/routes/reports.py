"""
Endpoints para reportes de alumnos y profesores
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, datetime
import logging

from app.database.session import get_db
from app.models.database_models import (
    Class, Student, Teacher, TeacherClass,
    WitnessReport, TeacherReport, Case, AIDailyPrediction
)
from app.schemas.common import ClassOut, MessageResponse
from app.schemas.student import StudentOut
from app.schemas.report import (
    WitnessReportCreate, WitnessReportOut,
    TeacherReportCreate, TeacherReportOut,
    StudentFeaturesOut
)
from app.core.security import get_current_user_id
from app.ml.predictor import predecir_bullying

logger = logging.getLogger(__name__)

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
    # Verificar que la clase existe (si se proporcionó)
    if report.class_id:
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


def ejecutar_prediccion_ml(student_id: int, fecha_reporte: date):
    """
    Tarea en segundo plano que ejecuta la predicción ML y guarda/actualiza ai_daily_predictions

    Args:
        student_id: ID del estudiante
        fecha_reporte: Fecha del reporte
    """
    from app.database.session import SessionLocal

    db = SessionLocal()
    try:
        logger.info(f"Iniciando predicción ML para estudiante {student_id} en fecha {fecha_reporte}")

        # 1. Ejecutar predicción
        resultado = predecir_bullying(db, student_id, fecha_reporte)

        # 2. Buscar predicción existente para este estudiante y fecha
        prediccion_existente = (
            db.query(AIDailyPrediction)
            .filter(
                AIDailyPrediction.student_id == student_id,
                AIDailyPrediction.date == fecha_reporte
            )
            .first()
        )

        if prediccion_existente:
            # Actualizar predicción existente
            prediccion_existente.bullying_probability = resultado["bullying_probability"]
            prediccion_existente.is_alert = resultado["is_alert"]
            prediccion_existente.risk_factors = resultado["risk_factors"]
            logger.info(f"Predicción actualizada para estudiante {student_id}: prob={resultado['bullying_probability']:.3f}, alert={resultado['is_alert']}")
        else:
            # Crear nueva predicción
            nueva_prediccion = AIDailyPrediction(
                student_id=student_id,
                date=fecha_reporte,
                bullying_probability=resultado["bullying_probability"],
                is_alert=resultado["is_alert"],
                risk_factors=resultado["risk_factors"]
            )
            db.add(nueva_prediccion)
            logger.info(f"Nueva predicción creada para estudiante {student_id}: prob={resultado['bullying_probability']:.3f}, alert={resultado['is_alert']}")

        db.commit()

    except Exception as e:
        logger.error(f"Error en predicción ML para estudiante {student_id}: {e}")
        db.rollback()
    finally:
        db.close()


@router.post("/teacher", response_model=MessageResponse)
def create_teacher_report(
    report: TeacherReportCreate,
    background_tasks: BackgroundTasks,
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Crea un reporte de observación docente y ejecuta predicción ML en segundo plano

    Args:
        report: Datos del reporte con métricas
        background_tasks: Manejador de tareas asíncronas
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

    fecha_reporte = report.event_date or date.today()

    new_report = TeacherReport(
        teacher_id=teacher_id,
        student_id=report.student_id,
        subject_id=report.subject_id,
        date=fecha_reporte,
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

    # Verificar si existe un caso abierto para este estudiante
    open_case = (
        db.query(Case)
        .filter(
            Case.student_id == report.student_id,
            Case.closed_at.is_(None)
        )
        .first()
    )

    # Si no existe un caso abierto, crear uno nuevo
    if not open_case:
        new_case = Case(
            student_id=report.student_id,
            opened_at=fecha_reporte,
            status=None
        )
        db.add(new_case)
        db.commit()

    # Ejecutar predicción ML en segundo plano
    background_tasks.add_task(ejecutar_prediccion_ml, report.student_id, fecha_reporte)

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
