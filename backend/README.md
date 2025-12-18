# Escudo Escolar - Backend API

<p align='left'>
    <a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff" alt="Python"></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white" alt="FastAPI"></a>
    <a href="https://www.postgresql.org"><img src="https://img.shields.io/badge/PostgreSQL-%23316192.svg?logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
    <a href="https://sqlalchemy.org"><img src="https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"></a>
    <a href="https://jwt.io/"><img src="https://img.shields.io/badge/JWT-000000?logo=jsonwebtokens&logoColor=white" alt="JWT"></a>
    <a href="https://scikit-learn.org/"><img src="https://img.shields.io/badge/scikit--learn-%23F7931E?logo=scikit-learn&logoColor=white" alt="scikit-learn"></a>
    <a href="https://xgboost.readthedocs.io/"><img src="https://img.shields.io/badge/XGBoost-337AB7?logo=xgboost&logoColor=white" alt="XGBoost"></a>
    <a href="https://www.langchain.com/"><img src="https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white" alt="LangChain"></a>
    <a href="https://openai.com"><img src="https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white" alt="OpenAI"></a>
    <a href="https://pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=white" alt="Pydantic"></a>
</p>

API REST para el sistema de detección temprana de bullying escolar con inteligencia artificial.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [API Endpoints](#api-endpoints)
- [Documentación Interactiva](#documentación-interactiva)
- [Modelo de Base de Datos](#modelo-de-base-de-datos)
- [Machine Learning](#machine-learning)
- [Autenticación](#autenticación)
- [Desarrollo](#desarrollo)
- [Licencia](#licencia)

## Descripción

El backend de Escudo Escolar es una API REST construida con FastAPI que proporciona:

- Sistema de autenticación JWT para profesores
- Gestión de reportes (testigos y profesores)
- Predicción de riesgo de bullying con Machine Learning
- Dashboard con visualizaciones (heatmap, timeline)
- Gestión de casos de estudiantes
- Integración con chatbot de apoyo emocional

## Arquitectura

```mermaid
graph TB
    subgraph "API Layer"
        A[FastAPI Router]
        B[Middleware]
        C[Dependency Injection]
    end

    subgraph "Business Logic"
        D[Auth Service]
        E[Reports Service]
        F[Dashboard Service]
        G[ML Predictor]
    end

    subgraph "Data Layer"
        H[SQLAlchemy ORM]
        I[(PostgreSQL)]
    end

    subgraph "External Services"
        J[OpenAI API]
        K[LangChain/LangGraph]
    end

    A --> D
    A --> E
    A --> F

    D --> H
    E --> H
    F --> H
    E --> G

    G --> H
    H --> I

    K --> J

    style A fill:#009485
    style I fill:#316192
    style G fill:#337ab7
```

## Tecnologías

- **Framework**: FastAPI 0.115.6
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy 2.0.36
- **Validación**: Pydantic 2.10.4
- **Autenticación**: JWT (python-jose 3.3.0)
- **Seguridad**: Passlib + Bcrypt 5.0.0
- **ML**:
  - XGBoost 2.1.3
  - scikit-learn 1.6.0
  - pandas 2.2.3
  - numpy 2.2.1
- **AI**:
  - OpenAI 1.59.5
  - LangChain 0.3.13
  - LangGraph 0.2.59
- **Gestor de Paquetes**: uv
- **ASGI Server**: Uvicorn 0.34.0

## Estructura del Proyecto

```
backend/
├── main.py                      # Punto de entrada de la aplicación
├── pyproject.toml               # Configuración de dependencias (uv/pip)
├── .env                         # Variables de entorno (NO versionar)
├── .env.example                 # Plantilla de variables de entorno
├── create_test_users.py         # Script para crear usuarios de prueba
│
├── app/
│   ├── core/                    # Configuración central
│   │   ├── config.py           # Settings con Pydantic
│   │   └── security.py         # JWT, hashing, autenticación
│   │
│   ├── database/               # Configuración de base de datos
│   │   └── session.py          # Engine, SessionLocal, get_db
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   └── database_models.py  # Todas las tablas
│   │
│   ├── schemas/                # Schemas Pydantic
│   │   ├── auth.py            # Login, Token
│   │   ├── case.py            # CaseOut, CaseCreate, CaseUpdate
│   │   ├── common.py          # ClassOut, MessageResponse
│   │   ├── report.py          # WitnessReport, TeacherReport
│   │   ├── student.py         # StudentOut
│   │   └── teacher.py         # TeacherOut
│   │
│   ├── routes/                 # Endpoints de la API
│   │   ├── health.py          # Health check
│   │   ├── auth.py            # Login de profesores
│   │   ├── reports.py         # Reportes de testigos y profesores
│   │   ├── dashboard.py       # Heatmap, timeline, casos
│   │   └── chat.py            # Proxy al chatbot
│   │
│   └── ml/                     # Machine Learning
│       └── predictor.py        # Modelo XGBoost para predicción
│
└── docs/
    └── images/                 # Capturas de pantalla
        ├── swagger-ui.png
        └── api-endpoints.png
```

## Instalación

### Prerequisitos

- Python 3.11+
- PostgreSQL 14+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes rápido)

Instalar `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Instalar Dependencias

Desde la **raíz del proyecto** (no desde `backend/`):

```bash
uv sync
```

Esto instalará automáticamente todas las dependencias definidas en `pyproject.toml`.

## Configuración

### Variables de Entorno

Crear archivo `.env` en el directorio `backend/`:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
# Database
DATABASE_URL=postgresql://usuario:password@host:5432/database

# Security
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria_para_jwt

# OpenAI (opcional, para chatbot)
OPENAI_API_KEY=sk-...

# CORS (opcional)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Base de Datos

#### Scripts SQL

```bash
# Ejecutar scripts de creación
psql -U usuario -d database -f ../data/database/01_create_database.sql
psql -U usuario -d database -f ../data/database/02_create_user.sql
psql -U usuario -d database -f ../data/database/03_insert_demo_data.sql
```

## Ejecución

### Desarrollo (con hot reload)

```bash
cd backend
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

O directamente:

```bash
uv run python main.py
```

### Producción

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/health` | Estado del API y base de datos | No |

### Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/auth/login` | Login de profesores (retorna JWT) | No |

**Request body**:
```json
{
  "email": "admin@escudoescolar.demo",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Reportes

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/reports/student/courses` | Lista de clases | No |
| POST | `/reports/student` | Crear reporte de testigo | No |
| GET | `/reports/teacher/courses` | Clases del profesor | Sí |
| GET | `/reports/teacher/students/{class_id}` | Estudiantes de una clase | Sí |
| POST | `/reports/teacher` | Crear reporte de profesor | Sí |
| GET | `/reports/features/{student_id}` | Features para ML | No |

### Dashboard

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/dashboard/heatmap` | Mapa de calor de reportes | Sí |
| GET | `/dashboard/timeline/{student_id}` | Timeline de estudiante | Sí |
| GET | `/dashboard/alerts` | Estudiantes con alertas | Sí |
| GET | `/dashboard/case/{case_id}` | Detalle de un caso | Sí |
| PUT | `/dashboard/case/{case_id}` | Actualizar caso | Sí |
| POST | `/dashboard/case` | Crear nuevo caso | Sí |

### Chatbot

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/chatbot` | Enviar mensaje al chatbot | No |
| GET | `/api/chatbot/health` | Estado del chatbot | No |

## Documentación Interactiva

FastAPI genera documentación interactiva automáticamente:

### Swagger UI
<img src="docs/images/swagger-ui.png" width="800" alt="Swagger UI">

Accede a http://localhost:8000/docs para:
- Ver todos los endpoints
- Probar la API directamente
- Ver schemas de request/response
- Autorizar con JWT

### ReDoc

Accede a http://localhost:8000/redoc para documentación alternativa.

## Modelo de Base de Datos

```mermaid
erDiagram
    TEACHERS ||--o{ TEACHER_CLASSES : "teaches"
    TEACHERS ||--o{ TEACHER_REPORTS : "creates"
    CLASSES ||--o{ STUDENTS : "contains"
    CLASSES ||--o{ TEACHER_CLASSES : "assigned to"
    CLASSES ||--o{ WITNESS_REPORTS : "reported in"
    STUDENTS ||--o{ TEACHER_REPORTS : "reported on"
    STUDENTS ||--o{ CASES : "has"
    STUDENTS ||--o{ AI_DAILY_PREDICTIONS : "predicted for"
    SUBJECTS ||--o{ TEACHER_REPORTS : "subject of"

    TEACHERS {
        int id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        boolean is_admin
    }

    CLASSES {
        int id PK
        string name
        string grade
    }

    STUDENTS {
        int id PK
        int class_id FK
        string first_name
        string last_name
        date birth_date
    }

    TEACHER_REPORTS {
        int id PK
        int teacher_id FK
        int student_id FK
        int subject_id FK
        date date
        int disengagement
        int social_isolation
        int peer_exclusion
        int emotional_reactivity
        int inhibition
        int physical_damage
        int intuition
        text notes
    }

    WITNESS_REPORTS {
        int id PK
        int class_id FK
        date date
    }

    CASES {
        int id PK
        int student_id FK
        date opened_at
        date closed_at
        string status
        text psychologist_notes
        text final_diagnosis
    }

    AI_DAILY_PREDICTIONS {
        int id PK
        int student_id FK
        date date
        float bullying_probability
        boolean is_alert
        jsonb risk_factors
    }
```

## Machine Learning

### Modelo de Predicción

El sistema utiliza un modelo **XGBoost** entrenado para predecir la probabilidad de bullying basándose en:

**Features**:
- Promedio de aislamiento social
- Promedio de exclusión entre pares
- Promedio de reactividad emocional
- Promedio de desconexión
- Promedio de inhibición
- Promedio de daño físico
- Promedio de intuición docente
- Número total de reportes

**Proceso**:

```mermaid
sequenceDiagram
    participant R as Report Endpoint
    participant BG as Background Task
    participant ML as ML Predictor
    participant DB as Database

    R->>BG: Crear tarea de predicción
    BG->>ML: predecir_bullying(student_id, date)
    ML->>DB: Obtener reportes históricos
    DB-->>ML: Features agregados
    ML->>ML: model.predict_proba()
    ML->>DB: Guardar/Actualizar ai_daily_predictions
    alt Probabilidad > 0.7
        ML->>DB: is_alert = True
    end
```

**Umbrales**:
- Probabilidad > 0.7 → Alerta alta
- Probabilidad 0.5-0.7 → Alerta media
- Probabilidad < 0.5 → Sin alerta

## Autenticación

### JWT (JSON Web Tokens)

El sistema usa JWT para autenticar profesores:

1. **Login**: POST `/auth/login` con email y password
2. **Recibir**: Token JWT en el response
3. **Usar**: Incluir en header: `Authorization: Bearer {token}`

### Ejemplo con cURL

```bash
# 1. Login
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@escudoescolar.demo","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Usar token
curl -X GET "http://localhost:8000/dashboard/heatmap" \
  -H "Authorization: Bearer $TOKEN"
```

### Usuarios de Prueba

| Email | Contraseña | Admin | Nombre |
|-------|-----------|-------|---------|
| `gustavo.debasica@escudoescolar.demo` | `password123` | Sí | Gustavo de Básica |
| `maripi.olet@escudoescolar.demo` | `password123` | No | Maripi Olet |

## Desarrollo

### Agregar un Nuevo Endpoint

1. Crear el schema Pydantic en `app/schemas/`
2. Crear la ruta en `app/routes/`
3. Registrar el router en `main.py`:

```python
from app.routes import my_new_route

app.include_router(my_new_route.router)
```

### Agregar un Nuevo Modelo

1. Definir el modelo SQLAlchemy en `app/models/database_models.py`
2. Crear migración con Alembic (si es necesario)
3. Crear schema Pydantic correspondiente

### Estructura de un Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import get_current_user_id
from app.schemas.my_schema import MySchema

router = APIRouter(prefix="/my-endpoint", tags=["My Tag"])

@router.get("/", response_model=MySchema)
def my_endpoint(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Lógica del endpoint
    return data
```

### Testing

```bash
# Instalar dependencias de desarrollo
uv sync --dev

# Ejecutar tests (cuando se implementen)
uv run pytest
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.

```
MIT License

Copyright (c) 2025 Escudo Escolar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

Ver [README principal](../README.md) para más información sobre el proyecto completo.
