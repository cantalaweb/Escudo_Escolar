"""
Endpoints para el Dashboard de Administración
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from collections import defaultdict

from app.database.session import get_db
from app.models.database_models import (
    Student, Teacher, TeacherReport, WitnessReport,
    AIDailyPrediction, Class, Case
)
from app.core.security import get_current_user_id
from app.schemas.case import CaseOut, CaseCreate, CaseUpdate
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_category_scores(report: TeacherReport) -> Dict[str, Any]:
    """Calcula los scores por categoría para un reporte"""
    return {
        "A": {  # Social
            "total": (report.social_isolation or 0) + (report.peer_exclusion or 0),
            "max": max(report.social_isolation or 0, report.peer_exclusion or 0),
            "metrics": {
                "social_isolation": report.social_isolation or 0,
                "peer_exclusion": report.peer_exclusion or 0
            }
        },
        "B": {  # Conductual
            "total": (report.emotional_reactivity or 0) + (report.inhibition or 0),
            "max": max(report.emotional_reactivity or 0, report.inhibition or 0),
            "metrics": {
                "emotional_reactivity": report.emotional_reactivity or 0,
                "inhibition": report.inhibition or 0
            }
        },
        "C": {  # Desenganche
            "total": (report.disengagement or 0) + (report.physical_damage or 0),
            "max": max(report.disengagement or 0, report.physical_damage or 0),
            "metrics": {
                "disengagement": report.disengagement or 0,
                "physical_damage": report.physical_damage or 0
            }
        },
        "D": {  # Control/Intuición
            "total": report.intuition or 0,
            "max": report.intuition or 0,
            "metrics": {
                "intuition": report.intuition or 0
            }
        }
    }


def determine_dominant_category(categories: Dict[str, Any]) -> tuple:
    """Determina la categoría dominante según los criterios especificados"""
    # Ordenar por total, luego por max, luego alfabéticamente
    sorted_cats = sorted(
        categories.items(),
        key=lambda x: (x[1]['total'], x[1]['max'], x[0]),
        reverse=True
    )

    dominant = sorted_cats[0][0]
    active_count = sum(1 for _, data in categories.items() if data['total'] > 0)

    return dominant, active_count


# =============================================================================
# HEATMAP DATA
# =============================================================================

@router.get("/heatmap")
def get_heatmap_data(
    days: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene datos para el mapa de calor

    Args:
        days: Número de días a mostrar (default: 30)
        start_date: Fecha inicial (opcional, se calcula desde end_date - days)
        end_date: Fecha final (opcional, default: hoy)

    Returns:
        Lista de estudiantes con sus reportes por día
    """
    # Verificar que el usuario es admin
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher or not teacher.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder al dashboard"
        )

    # Establecer rango de fechas
    if not end_date:
        end_date = date.today()

    if not start_date:
        # Si se proporciona 'days', usarlo; si no, usar 30 por defecto
        num_days = days if days is not None else 30
        start_date = end_date - timedelta(days=num_days - 1)

    # Query optimizada: obtener todos los reportes agrupados en una sola consulta
    reports_query = (
        db.query(
            Student.id.label('student_id'),
            Student.name.label('student_name'),
            Class.name.label('class_name'),
            TeacherReport.date,
            func.count(TeacherReport.id).label('count'),
            func.max(func.greatest(
                TeacherReport.social_isolation,
                TeacherReport.peer_exclusion,
                TeacherReport.emotional_reactivity,
                TeacherReport.inhibition,
                TeacherReport.disengagement,
                TeacherReport.physical_damage,
                TeacherReport.intuition
            )).label('max_severity')
        )
        .join(TeacherReport, Student.id == TeacherReport.student_id)
        .outerjoin(Class, Student.class_id == Class.id)
        .filter(TeacherReport.date.between(start_date, end_date))
        .group_by(Student.id, Student.name, Class.name, TeacherReport.date)
        .order_by(Student.id, TeacherReport.date)
        .all()
    )

    # Agrupar resultados por estudiante
    students_data = {}
    for row in reports_query:
        student_id = row.student_id

        if student_id not in students_data:
            students_data[student_id] = {
                "student_id": student_id,
                "student_name": row.student_name,
                "class_name": row.class_name or "Sin clase",
                "daily_data": {}
            }

        students_data[student_id]["daily_data"][row.date.isoformat()] = {
            "count": row.count,
            "severity": row.max_severity or 0
        }

    result = list(students_data.values())

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "students": result
    }


# =============================================================================
# SCATTER PLOT DATA (Risk Matrix)
# =============================================================================

@router.get("/risk-matrix")
def get_risk_matrix_data(
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene datos para la matriz de riesgo (scatter plot)

    Returns:
        Lista de estudiantes con total de reportes y probabilidad de bullying
    """
    # Verificar que el usuario es admin
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher or not teacher.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder al dashboard"
        )

    # Subconsulta para obtener la predicción más reciente de cada estudiante
    latest_predictions = (
        db.query(
            AIDailyPrediction.student_id,
            AIDailyPrediction.bullying_probability
        )
        .distinct(AIDailyPrediction.student_id)
        .order_by(AIDailyPrediction.student_id, AIDailyPrediction.date.desc())
        .subquery()
    )

    # Query optimizada con JOINs - obtiene todo en una sola consulta
    results = (
        db.query(
            Student.id,
            Student.name,
            Class.name.label('class_name'),
            func.count(TeacherReport.id).label('report_count'),
            func.coalesce(latest_predictions.c.bullying_probability, 0).label('probability')
        )
        .outerjoin(Class, Student.class_id == Class.id)
        .outerjoin(TeacherReport, Student.id == TeacherReport.student_id)
        .outerjoin(latest_predictions, Student.id == latest_predictions.c.student_id)
        .group_by(Student.id, Student.name, Class.name, latest_predictions.c.bullying_probability)
        .having(func.count(TeacherReport.id) > 0)
        .all()
    )

    # Formatear resultados
    return {
        "students": [
            {
                "student_id": row.id,
                "student_name": row.name,
                "class_name": row.class_name or "Sin clase",
                "report_count": row.report_count,
                "bullying_probability": round(row.probability * 100, 2)
            }
            for row in results
        ]
    }


# =============================================================================
# STUDENT TIMELINE DATA
# =============================================================================

@router.get("/student/{student_id}/timeline")
def get_student_timeline(
    student_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    source: str = Query("all", regex="^(teachers|witnesses|all)$"),
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene la línea temporal de un estudiante con todos los reportes y predicciones

    Args:
        student_id: ID del estudiante
        start_date: Fecha inicial (opcional)
        end_date: Fecha final (opcional)
        source: Fuente de datos ("teachers", "witnesses", "all")
    """
    # Verificar que el usuario es admin
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher or not teacher.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder al dashboard"
        )

    # Verificar que el estudiante existe
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {student_id} no encontrado"
        )

    # Establecer rango de fechas por defecto
    if not end_date:
        end_date = date.today()
    if not start_date:
        # Calcular el inicio del año escolar (1 de septiembre)
        # Si estamos antes de septiembre, el año escolar empezó el septiembre pasado
        current_year = end_date.year
        school_year_start = date(current_year, 9, 1)

        # Si hoy es antes del 1 de septiembre, el año escolar actual empezó el año pasado
        if end_date < school_year_start:
            school_year_start = date(current_year - 1, 9, 1)

        start_date = school_year_start

    # Obtener reportes de profesores agrupados por fecha
    teacher_reports_by_date = defaultdict(list)
    if source in ["teachers", "all"]:
        teacher_reports = (
            db.query(TeacherReport)
            .filter(
                TeacherReport.student_id == student_id,
                TeacherReport.date.between(start_date, end_date)
            )
            .all()
        )

        for report in teacher_reports:
            teacher_reports_by_date[report.date].append(report)

    # Obtener reportes de testigos (clase del estudiante)
    witness_count_by_date = {}
    if source in ["witnesses", "all"] and student.class_id:
        witness_reports = (
            db.query(
                WitnessReport.date,
                func.count(WitnessReport.id).label('count')
            )
            .filter(
                WitnessReport.class_id == student.class_id,
                WitnessReport.date.between(start_date, end_date)
            )
            .group_by(WitnessReport.date)
            .all()
        )

        for report in witness_reports:
            witness_count_by_date[report.date] = report.count

    # Obtener predicciones de IA
    ai_predictions = (
        db.query(AIDailyPrediction)
        .filter(
            AIDailyPrediction.student_id == student_id,
            AIDailyPrediction.date.between(start_date, end_date)
        )
        .all()
    )

    ai_predictions_by_date = {pred.date: pred for pred in ai_predictions}

    # Obtener todos los casos del estudiante
    student_cases = (
        db.query(Case)
        .filter(Case.student_id == student_id)
        .order_by(Case.opened_at)
        .all()
    )


    # Construir timeline
    timeline = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()

        # Buscar el caso que corresponde a esta fecha
        associated_case = None
        for case in student_cases:
            if case.opened_at <= current_date:
                # Si el caso está abierto o cerrado después de esta fecha
                if case.closed_at is None or case.closed_at >= current_date:
                    associated_case = case
                    break

        # Datos del día
        day_data = {
            "date": date_str,
            "teacher_reports": [],
            "witness_reports_count": witness_count_by_date.get(current_date, 0),
            "ai_prediction": None,
            "case": {
                "id": associated_case.id,
                "opened_at": associated_case.opened_at.isoformat(),
                "closed_at": associated_case.closed_at.isoformat() if associated_case.closed_at else None,
                "status": associated_case.status,
                "psychologist_notes": associated_case.psychologist_notes,
                "final_diagnosis": associated_case.final_diagnosis
            } if associated_case else None,
            "categories": {"A": 0, "B": 0, "C": 0, "D": 0},
            "dominant_category": None,
            "active_categories_count": 0,
            "total_severity": 0
        }

        # Procesar reportes de profesores
        if current_date in teacher_reports_by_date:
            aggregated_categories = {"A": {"total": 0, "max": 0},
                                    "B": {"total": 0, "max": 0},
                                    "C": {"total": 0, "max": 0},
                                    "D": {"total": 0, "max": 0}}

            for report in teacher_reports_by_date[current_date]:
                categories = calculate_category_scores(report)

                # Agregar a totales
                for cat in ["A", "B", "C", "D"]:
                    aggregated_categories[cat]["total"] += categories[cat]["total"]
                    aggregated_categories[cat]["max"] = max(
                        aggregated_categories[cat]["max"],
                        categories[cat]["max"]
                    )

                # Agregar reporte individual
                day_data["teacher_reports"].append({
                    "id": report.id,
                    "teacher_name": report.teacher.name if report.teacher else "Anónimo",
                    "subject_name": report.subject.name if report.subject else "N/A",
                    "metrics": {
                        "social_isolation": report.social_isolation or 0,
                        "peer_exclusion": report.peer_exclusion or 0,
                        "emotional_reactivity": report.emotional_reactivity or 0,
                        "inhibition": report.inhibition or 0,
                        "disengagement": report.disengagement or 0,
                        "physical_damage": report.physical_damage or 0,
                        "intuition": report.intuition or 0
                    },
                    "notes": report.notes,
                    "categories": categories
                })

            # Determinar categoría dominante
            dominant, active_count = determine_dominant_category(aggregated_categories)
            day_data["dominant_category"] = dominant
            day_data["active_categories_count"] = active_count
            day_data["categories"] = {
                cat: data["total"] for cat, data in aggregated_categories.items()
            }
            day_data["total_severity"] = sum(data["total"] for data in aggregated_categories.values())

        # Agregar predicción de IA si existe
        if current_date in ai_predictions_by_date:
            pred = ai_predictions_by_date[current_date]
            day_data["ai_prediction"] = {
                "bullying_probability": pred.bullying_probability,
                "is_alert": pred.is_alert,
                "risk_factors": pred.risk_factors
            }

        # Solo agregar días con datos
        if (day_data["teacher_reports"] or
            day_data["witness_reports_count"] > 0 or
            day_data["ai_prediction"]):
            timeline.append(day_data)

        current_date += timedelta(days=1)

    return {
        "student_id": student_id,
        "student_name": student.name,
        "class_name": student.class_.name if student.class_ else "Sin clase",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timeline": timeline
    }


# =============================================================================
# STUDENT RADAR DATA
# =============================================================================

@router.get("/student/{student_id}/radar")
def get_student_radar(
    student_id: int,
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene datos para el gráfico radar del estudiante

    Returns:
        Promedios por categoría del estudiante vs promedio de su clase
    """
    # Verificar que el usuario es admin
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher or not teacher.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder al dashboard"
        )

    # Verificar que el estudiante existe
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {student_id} no encontrado"
        )

    # Calcular promedios del estudiante
    student_stats = db.query(
        func.avg(TeacherReport.social_isolation).label('avg_social_isolation'),
        func.avg(TeacherReport.peer_exclusion).label('avg_peer_exclusion'),
        func.avg(TeacherReport.emotional_reactivity).label('avg_emotional_reactivity'),
        func.avg(TeacherReport.inhibition).label('avg_inhibition'),
        func.avg(TeacherReport.disengagement).label('avg_disengagement'),
        func.avg(TeacherReport.physical_damage).label('avg_physical_damage'),
        func.avg(TeacherReport.intuition).label('avg_intuition'),
    ).filter(TeacherReport.student_id == student_id).first()

    # Calcular promedios de la clase
    class_stats = None
    if student.class_id:
        class_students = db.query(Student.id).filter(Student.class_id == student.class_id).all()
        class_student_ids = [s.id for s in class_students]

        class_stats = db.query(
            func.avg(TeacherReport.social_isolation).label('avg_social_isolation'),
            func.avg(TeacherReport.peer_exclusion).label('avg_peer_exclusion'),
            func.avg(TeacherReport.emotional_reactivity).label('avg_emotional_reactivity'),
            func.avg(TeacherReport.inhibition).label('avg_inhibition'),
            func.avg(TeacherReport.disengagement).label('avg_disengagement'),
            func.avg(TeacherReport.physical_damage).label('avg_physical_damage'),
            func.avg(TeacherReport.intuition).label('avg_intuition'),
        ).filter(TeacherReport.student_id.in_(class_student_ids)).first()

    # Construir datos del radar
    student_data = {
        "A_Social": round(
            (float(student_stats.avg_social_isolation or 0) +
             float(student_stats.avg_peer_exclusion or 0)) / 2,
            2
        ),
        "B_Conductual": round(
            (float(student_stats.avg_emotional_reactivity or 0) +
             float(student_stats.avg_inhibition or 0)) / 2,
            2
        ),
        "C_Desenganche": round(
            (float(student_stats.avg_disengagement or 0) +
             float(student_stats.avg_physical_damage or 0)) / 2,
            2
        ),
        "D_Intuicion": round(float(student_stats.avg_intuition or 0), 2)
    }

    class_data = None
    if class_stats:
        class_data = {
            "A_Social": round(
                (float(class_stats.avg_social_isolation or 0) +
                 float(class_stats.avg_peer_exclusion or 0)) / 2,
                2
            ),
            "B_Conductual": round(
                (float(class_stats.avg_emotional_reactivity or 0) +
                 float(class_stats.avg_inhibition or 0)) / 2,
                2
            ),
            "C_Desenganche": round(
                (float(class_stats.avg_disengagement or 0) +
                 float(class_stats.avg_physical_damage or 0)) / 2,
                2
            ),
            "D_Intuicion": round(float(class_stats.avg_intuition or 0), 2)
        }

    return {
        "student_id": student_id,
        "student_name": student.name,
        "student_data": student_data,
        "class_average": class_data
    }


# =============================================================================
# CASE MANAGEMENT
# =============================================================================

@router.get("/case/{student_id}/{report_date}", response_model=CaseOut | None)
def get_case_for_date(
    student_id: int,
    report_date: date,
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene el caso asociado a un estudiante en una fecha específica

    Un reporte pertenece a un caso si su fecha está entre opened_at y closed_at.
    Si closed_at es NULL, el caso está abierto y todos los reportes desde opened_at pertenecen a él.

    Args:
        student_id: ID del estudiante
        report_date: Fecha del reporte
        teacher_id: ID del profesor (extraído del token JWT)
        db: Sesión de base de datos

    Returns:
        Información del caso o None si no hay caso para esa fecha
    """
    # Verificar que el usuario es admin
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher or not teacher.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a los casos"
        )

    # Buscar el caso que contiene esta fecha
    case = (
        db.query(Case)
        .filter(
            Case.student_id == student_id,
            Case.opened_at <= report_date,
            or_(
                Case.closed_at.is_(None),  # Caso abierto
                Case.closed_at >= report_date  # Caso cerrado pero incluye esta fecha
            )
        )
        .first()
    )

    return case


@router.put("/case/{case_id}", response_model=MessageResponse)
def update_case(
    case_id: int,
    case_update: CaseUpdate,
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Actualiza un caso existente

    Args:
        case_id: ID del caso
        case_update: Datos a actualizar
        teacher_id: ID del profesor (extraído del token JWT)
        db: Sesión de base de datos

    Returns:
        Mensaje de confirmación
    """
    # Verificar que el usuario es admin
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher or not teacher.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden actualizar casos"
        )

    # Buscar el caso
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caso con ID {case_id} no encontrado"
        )

    # Actualizar campos proporcionados
    if case_update.status is not None:
        case.status = case_update.status

    if case_update.psychologist_notes is not None:
        case.psychologist_notes = case_update.psychologist_notes

    if case_update.final_diagnosis is not None:
        case.final_diagnosis = case_update.final_diagnosis

    if case_update.closed_at is not None:
        case.closed_at = case_update.closed_at

    db.commit()

    return {
        "message": "Caso actualizado correctamente",
        "status": "success",
        "id": case_id
    }


@router.post("/case", response_model=CaseOut)
def create_case(
    case_create: CaseCreate,
    teacher_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo caso para un estudiante

    Args:
        case_create: Datos del nuevo caso
        teacher_id: ID del profesor (extraído del token JWT)
        db: Sesión de base de datos

    Returns:
        El caso creado
    """
    # Verificar que el usuario es admin
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher or not teacher.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear casos"
        )

    # Verificar que el estudiante existe
    student = db.query(Student).filter(Student.id == case_create.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {case_create.student_id} no encontrado"
        )

    # Crear el nuevo caso
    new_case = Case(
        student_id=case_create.student_id,
        opened_at=case_create.opened_at,
        closed_at=case_create.closed_at,
        status=case_create.status,
        psychologist_notes=case_create.psychologist_notes,
        final_diagnosis=case_create.final_diagnosis
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    return new_case
