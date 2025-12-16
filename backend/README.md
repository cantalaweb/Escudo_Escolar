# Escudo Escolar - Backend

Sistema de detección temprana de bullying escolar con inteligencia artificial.

## Tecnologías

- **Framework**: FastAPI 0.115+
- **Base de datos**: PostgreSQL (Render.com)
- **ORM**: SQLAlchemy 2.0
- **Autenticación**: JWT (python-jose)
- **Seguridad**: Bcrypt para hashing de contraseñas
- **IA**: OpenAI + LangChain + LangGraph (para el chatbot)

## Estructura del Proyecto

```
backend/
├── main.py                 # Punto de entrada de la aplicación
├── .env                    # Variables de entorno (NO versionar)
├── .env.example            # Plantilla de variables de entorno
├── requirements.txt        # Dependencias de Python
│
└── app/
    ├── core/              # Configuración y seguridad
    │   ├── config.py      # Settings con Pydantic
    │   └── security.py    # JWT, hashing de passwords
    │
    ├── database/          # Configuración de base de datos
    │   └── session.py     # SQLAlchemy engine y sesiones
    │
    ├── models/            # Modelos SQLAlchemy
    │   └── database_models.py
    │
    ├── schemas/           # Schemas Pydantic (validación)
    │   ├── auth.py
    │   ├── common.py
    │   ├── student.py
    │   ├── teacher.py
    │   └── report.py
    │
    ├── routes/            # Endpoints de la API
    │   ├── health.py
    │   ├── auth.py
    │   ├── chat.py
    │   ├── reports.py
    │   └── coordinator.py
    │
    └── services/          # Lógica de negocio (futuro)
```

## Instalación

### 1. Prerequisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes rápido)

Si no tienes `uv`, instálalo con:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalar dependencias

Desde la **raíz del proyecto** (no desde backend/), ejecuta:

```bash
uv sync
```

Esto instalará todas las dependencias tanto del proyecto raíz (ML) como del backend (API).

### 3. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y rellena las credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales reales:

```env
DATABASE_URL=postgresql://usuario:password@host/database
SECRET_KEY=tu_clave_secreta_para_jwt
OPENAI_API_KEY=tu_api_key_de_openai  # Opcional
```

### 4. Ejecutar la aplicación

Desde el directorio `backend/`:

**Desarrollo (con hot reload):**

```bash
uv run uvicorn main:app --reload
```

O directamente:

```bash
uv run python main.py
```

**Producción:**

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

> **Nota**: `uv run` usa automáticamente el entorno virtual del workspace

## Endpoints Principales

### Health Check

- `GET /api/health` - Verifica el estado del API y base de datos

### Autenticación

- `POST /auth/login` - Login de profesores (retorna JWT)

### Reportes

- `GET /reports/student/courses` - Lista de clases para reportes de testigos
- `POST /reports/student` - Crear reporte de testigo anónimo
- `GET /reports/teacher/courses` - Clases asignadas al profesor (requiere auth)
- `GET /reports/teacher/students/{class_id}` - Estudiantes de una clase (requiere auth)
- `POST /reports/teacher` - Crear reporte de observación docente (requiere auth)
- `GET /reports/features/{student_id}` - Features para el modelo ML

### Chatbot

- `POST /api/chat` - Endpoint del chatbot de apoyo emocional

### Coordinación

- `POST /coordinator/generate_summary` - Dispara análisis y generación de alertas

## Documentación Interactiva

Una vez ejecutada la aplicación, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usuarios de Prueba

El proyecto incluye un script para crear usuarios de prueba con contraseñas hasheadas correctamente.

### Crear/Actualizar usuarios de prueba:

```bash
uv run python create_test_users.py
```

### Usuarios disponibles:

| Email | Contraseña | Admin | Nombre |
|-------|-----------|-------|---------|
| `diego.vazquez@escudoescolar.demo` | `password123` | No | Diego Vazquez Dominguez |
| `maria.garcia@escudoescolar.demo` | `password123` | No | María García López |
| `admin@escudoescolar.demo` | `admin123` | **Sí** | Admin Principal |
| `carlos.ruiz@escudoescolar.demo` | `password123` | No | Carlos Ruiz Sánchez |
| `ana.martinez@escudoescolar.demo` | `password123` | No | Ana Martínez Pérez |

## Autenticación

La mayoría de endpoints de profesores requieren autenticación JWT:

1. Hacer login en `/auth/login` con email y password
2. Copiar el `access_token` del response
3. En Swagger UI, hacer click en "Authorize" e ingresar: `Bearer {access_token}`
4. O en requests, agregar header: `Authorization: Bearer {access_token}`

### Ejemplo de login:

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@escudoescolar.demo", "password": "admin123"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Base de Datos

La base de datos PostgreSQL está alojada en Render.com. El esquema incluye:

- **classes**: Clases/aulas
- **subjects**: Asignaturas
- **students**: Estudiantes
- **teachers**: Profesores
- **teacher_classes**: Relación profesores-clases
- **teacher_reports**: Reportes de observación docente (métricas)
- **witness_reports**: Reportes anónimos de testigos
- **ai_daily_predictions**: Predicciones del modelo
- **cases**: Gestión de casos confirmados

## Desarrollo

### Agregar un nuevo endpoint

1. Crear el schema en `app/schemas/`
2. Crear la ruta en `app/routes/`
3. Registrar el router en `main.py`

### Agregar un nuevo modelo

1. Crear el modelo SQLAlchemy en `app/models/database_models.py`
2. Crear migración con Alembic (si es necesario)

## Próximos Pasos

- [ ] Implementar el chatbot real con LangGraph
- [ ] Crear el modelo ML de detección de bullying
- [ ] Implementar sistema de notificaciones
- [ ] Agregar tests unitarios
- [ ] Configurar CI/CD
