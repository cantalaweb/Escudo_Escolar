"""
Modelos SQLAlchemy para la base de datos
Reflejan la estructura definida en los scripts SQL
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, Text, Float,
    Date, DateTime, SmallInteger, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime, date

from app.database.session import Base


# =============================================================================
# 1. ESTRUCTURA ACADÉMICA (ESTÁTICA)
# =============================================================================

class Class(Base):
    """Clases/Aulas (Ej: 'ESO 1º A')"""
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    students = relationship("Student", back_populates="class_")
    teacher_classes = relationship("TeacherClass", back_populates="class_")
    witness_reports = relationship("WitnessReport", back_populates="class_")


class Subject(Base):
    """Asignaturas (Ej: 'Matemáticas', 'Educación Física')"""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    # Relaciones
    teacher_reports = relationship("TeacherReport", back_populates="subject")


class Student(Base):
    """Alumnos"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    class_ = relationship("Class", back_populates="students")
    teacher_reports = relationship("TeacherReport", back_populates="student")
    ai_predictions = relationship("AIDailyPrediction", back_populates="student")
    cases = relationship("Case", back_populates="student")


class Teacher(Base):
    """Profesores"""
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    teacher_classes = relationship("TeacherClass", back_populates="teacher")
    teacher_reports = relationship("TeacherReport", back_populates="teacher")


class TeacherClass(Base):
    """Relación: Qué profesores dan clase a qué grupos"""
    __tablename__ = "teacher_classes"

    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), primary_key=True)

    # Relaciones
    teacher = relationship("Teacher", back_populates="teacher_classes")
    class_ = relationship("Class", back_populates="teacher_classes")


# =============================================================================
# 2. INPUTS DEL MODELO (DIARIO)
# =============================================================================

class TeacherReport(Base):
    """Reportes de Observación Docente - Fuente Principal de datos"""
    __tablename__ = "teacher_reports"

    id = Column(BigInteger, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)

    date = Column(Date, nullable=False, default=date.today, index=True)

    # Métricas Escala Likert (0-3)
    academic_performance = Column(SmallInteger, default=0)  # log_asis
    social_isolation = Column(SmallInteger, default=0)      # soc_aisl
    peer_exclusion = Column(SmallInteger, default=0)        # soc_excl
    emotional_reactivity = Column(SmallInteger, default=0)  # con_reac
    inhibition = Column(SmallInteger, default=0)            # con_inhib
    physical_damage = Column(SmallInteger, default=0)       # fis_mat
    intuition = Column(SmallInteger, default=0)             # intuicion

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    teacher = relationship("Teacher", back_populates="teacher_reports")
    student = relationship("Student", back_populates="teacher_reports")
    subject = relationship("Subject", back_populates="teacher_reports")


class WitnessReport(Base):
    """Reportes de Testigos - Fuente Secundaria"""
    __tablename__ = "witness_reports"

    id = Column(BigInteger, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    date = Column(Date, nullable=False, default=date.today, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    class_ = relationship("Class", back_populates="witness_reports")


# =============================================================================
# 3. CEREBRO DE LA IA Y GESTIÓN
# =============================================================================

class AIDailyPrediction(Base):
    """Histórico de Predicciones de la IA"""
    __tablename__ = "ai_daily_predictions"

    id = Column(BigInteger, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    date = Column(Date, nullable=False, default=date.today, index=True)

    bullying_probability = Column(Float, nullable=True)
    is_alert = Column(Boolean, default=False)

    # Feature Importance local (JSON)
    # Ej: {"testigos": "HIGH", "aislamiento": "MED"}
    risk_factors = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    student = relationship("Student", back_populates="ai_predictions")


class Case(Base):
    """Gestión de Casos - Ciclo de feedback humano"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)

    opened_at = Column(Date, default=date.today)
    closed_at = Column(Date, nullable=True)

    status = Column(
        String(50),
        nullable=True,
        # CHECK constraint manejado por Alembic/migraciones
    )

    psychologist_notes = Column(Text, nullable=True)
    final_diagnosis = Column(String(100), nullable=True)

    # Relaciones
    student = relationship("Student", back_populates="cases")
