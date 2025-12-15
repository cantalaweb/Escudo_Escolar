from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy import create_engine, func, text, Column, Integer, String, ForeignKey, DateTime, Date, Boolean, Text, Float, JSON, SmallInteger
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base

# ==============================================================================
# CONFIGURACIÓN DE BASE DE DATOS (POSTGRESQL - PROD)
# ==============================================================================

SQLALCHEMY_DATABASE_URL = "postgresql://backend_app:yHxJAu3BumdL9J_VWQnW@dpg-d4vg58fpm1nc73bo3qcg-a.frankfurt-postgres.render.com/escudo_escolar_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() 

# ==============================================================================
# DEPENDENCIAS
# ==============================================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==============================================================================
# MODELOS DE BASE DE DATOS (Reflejando el nuevo ERD)
# ==============================================================================

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(150), unique=True)
    pwd_hash = Column(String(255))
    is_admin = Column(Integer, default=0) 
    created_at = Column(DateTime, default=datetime.now)

class TeacherClass(Base):
    __tablename__ = "teacher_classes"
    class_id = Column(Integer, ForeignKey("classes.id"), primary_key=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), primary_key=True)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

class WitnessReport(Base):
    __tablename__ = "witness_reports"
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=date.today)
    class_id = Column(Integer, ForeignKey("classes.id"))
    created_at = Column(DateTime, default=datetime.now)

class TeacherReport(Base):
    __tablename__ = "teacher_reports"
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=date.today)
    
    # Factores de riesgo (Scores)
    academic_performance = Column(SmallInteger)
    social_isolation = Column(SmallInteger)
    peer_exclusion = Column(SmallInteger)
    emotional_reactivity = Column(SmallInteger)
    inhibition = Column(SmallInteger)
    physical_damage = Column(SmallInteger)
    intuition = Column(SmallInteger)
    
    notes = Column(Text, nullable=True)
    
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)

# ==============================================================================
# MOCK DE CADENA DE AGENTES
# ==============================================================================
class MockGraph:
    def invoke(self, inputs):
        return {'respuesta_final': f"Procesado por IA: {inputs.get('mensaje_entrada', '')}"}

app_graph = MockGraph()

# ==============================================================================
# INICIALIZACIÓN DE LA WEBAPP
# ==============================================================================
app = FastAPI(
    title="Escudo Escolar",
    description="Backend conectado a PostgreSQL Render.",
    version="1.1.0"
)

# ==============================================================================
# SCHEMAS PYDANTIC
# ==============================================================================

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CourseOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class StudentOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class ReportStudentRequest(BaseModel):
    course_id: int
    event_date: Optional[date] = None

class TeacherReportRequest(BaseModel):
    student_id: int
    academic_performance: int
    social_isolation: int
    peer_exclusion: int
    emotional_reactivity: int
    inhibition: int
    physical_damage: int
    intuition: int
    notes: Optional[str] = None
    event_date: Optional[date] = None

class SummaryTriggerRequest(BaseModel):
    period_start: Optional[date] = None
    period_end: Optional[date] = None

# ==============================================================================
# ENDPOINTS
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. CHATBOT Y HEALTH CHECK
# ------------------------------------------------------------------------------

@app.post("/api/chat")
async def chat(mensaje: str):
    inputs = {"mensaje_entrada": mensaje}
    resultado = app_graph.invoke(inputs)
    return {"respuesta": resultado['respuesta_final']}

@app.get("/api/health")
def health_check():
    return {"status": "online", "db": "PostgreSQL Render", "version": "1.1.0"}

# ------------------------------------------------------------------------------
# 2. AUTENTICACIÓN (/auth)
# ------------------------------------------------------------------------------

@app.post("/auth/login", response_model=Token)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.email == credentials.email).first()
    
    if not teacher:
        # En una app real lanzaríamos error 401 si no existe
        pass 
    
    user_id = teacher.id if teacher else "invitado"
    return {"access_token": f"token-jwt-user-{user_id}", "token_type": "bearer"}

# ------------------------------------------------------------------------------
# 3. REPORTES ALUMNOS (/reports/student) -> Tabla `witness_reports`
# ------------------------------------------------------------------------------

@app.get("/reports/student/courses", response_model=List[CourseOut])
async def get_courses_student(db: Session = Depends(get_db)):
    return db.query(Class).all()

@app.post("/reports/student")
async def create_student_report(report: ReportStudentRequest, db: Session = Depends(get_db)):
    db_report = WitnessReport(
        class_id=report.course_id,
        date=report.event_date or date.today()
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return {"message": "Reporte registrado", "status": "success", "id": db_report.id}

# ------------------------------------------------------------------------------
# 4. REPORTES PROFESORES (/reports/teacher) -> Tabla `teacher_reports`
# ------------------------------------------------------------------------------

@app.get("/reports/teacher/courses", response_model=List[CourseOut])
async def get_courses_teacher(teacher_email: str = "profesor@ejemplo.com", db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.email == teacher_email).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    classes = (
        db.query(Class)
        .join(TeacherClass, TeacherClass.class_id == Class.id)
        .filter(TeacherClass.teacher_id == teacher.id)
        .all()
    )
    return classes

@app.get("/reports/teacher/students/{course_id}", response_model=List[StudentOut])
async def get_students_by_course(course_id: int, db: Session = Depends(get_db)):
    return db.query(Student).filter(Student.class_id == course_id).all()

@app.post("/reports/teacher")
async def create_teacher_report(report: TeacherReportRequest, db: Session = Depends(get_db)):
    # En producción obtener ID del token. Aquí hardcodeamos el 1.
    teacher_id = 1 
    
    new_report = TeacherReport(
        student_id=report.student_id,
        teacher_id=teacher_id,
        date=report.event_date or date.today(),
        academic_performance=report.academic_performance,
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
    return {"message": "Reporte guardado correctamente", "status": "success"}

# ------------------------------------------------------------------------------
# 5. COORDINACIÓN
# ------------------------------------------------------------------------------

@app.post("/coordinator/generate_summary")
async def generate_summary(request: SummaryTriggerRequest):
    return {"message": "Proceso de análisis iniciado en Render", "job_id": "job_render_001"}

# ------------------------------------------------------------------------------
# 6. FEATURE EXTRACTION
# ------------------------------------------------------------------------------

@app.get("/api/features/{student_id}")
async def get_student_features(student_id: int, db: Session = Depends(get_db)):
    try:
        stats = db.query(
            func.avg(TeacherReport.social_isolation).label('avg_isolation'),
            func.avg(TeacherReport.peer_exclusion).label('avg_exclusion'),
            func.avg(TeacherReport.emotional_reactivity).label('avg_emotion'),
            func.count(TeacherReport.id).label('report_count')
        ).filter(TeacherReport.student_id == student_id).first()
        
        count = getattr(stats, 'report_count', 0) or 0
        
        return {
            "student_id": student_id,
            "features": {
                "avg_isolation": float(getattr(stats, 'avg_isolation', 0) or 0),
                "avg_exclusion": float(getattr(stats, 'avg_exclusion', 0) or 0),
                "avg_emotion": float(getattr(stats, 'avg_emotion', 0) or 0),
                "total_reports": int(count)
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
         return {"error": "Error consultando DB", "details": str(e)}

# ==============================================================================
# FINAL DEL ARCHIVO
# ==============================================================================
