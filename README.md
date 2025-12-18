<h1 align='center'>Escudo Escolar</h1>

<h3 align='center'>Sistema de detección temprana de bullying escolar mediante inteligencia artificial</h3>

<p align='center'>
    <a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff" alt="Python"></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white" alt="FastAPI"></a>
    <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-%2320232a.svg?logo=react&logoColor=%2361DAFB" alt="React"></a>
    <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-black?logo=next.js&logoColor=white" alt="Next.js"></a>
    <a href="https://www.postgresql.org"><img src="https://img.shields.io/badge/PostgreSQL-%23316192.svg?logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
    <a href="https://mui.com/"><img src="https://img.shields.io/badge/Material--UI-0081CB?logo=mui&logoColor=white" alt="Material-UI"></a>
    <a href="https://scikit-learn.org/"><img src="https://img.shields.io/badge/scikit--learn-%23F7931E?logo=scikit-learn&logoColor=white" alt="scikit-learn"></a>
    <a href="https://xgboost.readthedocs.io/"><img src="https://img.shields.io/badge/XGBoost-337AB7?logo=xgboost&logoColor=white" alt="XGBoost"></a>
    <a href="https://www.langchain.com/"><img src="https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white" alt="LangChain"></a>
    <a href="https://openai.com"><img src="https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white" alt="OpenAI"></a>
    <a href="https://pandas.pydata.org"><img src="https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=fff" alt="Pandas"></a>
    <a href="https://numpy.org"><img src="https://img.shields.io/badge/NumPy-4DABCF?logo=numpy&logoColor=fff" alt="NumPy"></a>
    <a href="https://sqlalchemy.org"><img src="https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"></a>
    <a href="https://jwt.io/"><img src="https://img.shields.io/badge/JWT-000000?logo=jsonwebtokens&logoColor=white" alt="JWT"></a>
</p>

## Tabla de Contenidos

- [Introducción](#introducción)
- [Características](#características)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Capturas de Pantalla](#capturas-de-pantalla)
- [Tecnologías](#tecnologías)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Flujo de Datos](#flujo-de-datos)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Agradecimientos](#agradecimientos)

## Introducción

**Escudo Escolar** es un sistema integral de detección temprana de bullying escolar que combina machine learning, análisis de comportamiento y apoyo emocional mediante IA. El sistema permite a profesores y personal educativo monitorizar el bienestar de los estudiantes, detectar patrones de riesgo y gestionar casos de manera eficiente.

El proyecto consta de tres componentes principales:
1. **Backend API** (FastAPI + PostgreSQL + ML)
2. **Frontend Web** (Next.js + React + Material-UI)
3. **Chatbot de Apoyo** (LangChain + OpenAI)

## Características

- **Sistema de Reportes Dual**
  - Reportes anónimos de testigos/estudiantes
  - Reportes detallados de profesores con métricas de comportamiento

- **Dashboard Interactivo**
  - Mapa de calor (heatmap) con visualización de reportes por estudiante y fecha
  - Timeline individual de cada estudiante
  - Gestión visual de casos (apertura, seguimiento, cierre)

- **Predicción con Machine Learning**
  - Modelo XGBoost entrenado para detectar patrones de bullying
  - Cálculo automático de probabilidad de riesgo
  - Generación de alertas para casos de alto riesgo

- **Chatbot de Apoyo Emocional**
  - Asistente virtual "Alex" para estudiantes
  - Sistema multi-agente con LangChain y LangGraph
  - Conversaciones privadas y confidenciales

- **Autenticación y Seguridad**
  - Sistema JWT para profesores
  - Reportes anónimos sin autenticación
  - Hashing de contraseñas con bcrypt

## Arquitectura del Sistema

```mermaid
graph TB
    subgraph "Frontend - Next.js"
        A[Landing Page]
        B[Login Profesores]
        C[Dashboard Panel]
        D[Chatbot Alex]
        E[Formularios Reportes]
    end

    subgraph "Backend - FastAPI"
        F[API REST]
        G[Auth JWT]
        H[ML Predictor]
        I[Chatbot Service]
    end

    subgraph "Data Layer"
        J[(PostgreSQL)]
        K[SQLAlchemy ORM]
    end

    subgraph "AI Services"
        L[OpenAI GPT]
        M[LangChain/LangGraph]
        N[XGBoost Model]
    end

    A --> F
    B --> G
    C --> F
    D --> I
    E --> F

    F --> K
    G --> K
    H --> N
    I --> M

    K --> J
    M --> L
    H --> K

    style F fill:#009485
    style C fill:#61dafb
    style J fill:#316192
    style N fill:#337ab7
```

## Capturas de Pantalla

### Landing Page
<img src="docs/images/landing-page.png" width="800" alt="Landing Page">

### Dashboard - Mapa de Calor
<img src="docs/images/dashboard-heatmap.png" width="800" alt="Dashboard Heatmap">

### Timeline de Estudiante
<img src="docs/images/dashboard-timeline.png" width="800" alt="Timeline">

### Gestión de Casos
<img src="docs/images/case-management.png" width="800" alt="Case Management">

### Chatbot Alex
<img src="docs/images/chatbot-interface.png" width="800" alt="Chatbot">

### Formularios de Reporte
<img src="docs/images/teacher-report-form.png" width="600" alt="Teacher Report">
<img src="docs/images/witness-report-form.png" width="600" alt="Witness Report">

## Tecnologías

### Backend
- **Framework**: FastAPI 0.115+
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Autenticación**: JWT (python-jose), bcrypt
- **ML**: XGBoost, scikit-learn, pandas, numpy
- **AI**: OpenAI, LangChain, LangGraph

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **UI Library**: React 19
- **Components**: Material-UI (MUI) 6
- **Styling**: CSS-in-JS (Emotion)
- **HTTP Client**: Fetch API

### Chatbot
- **Framework**: LangChain + LangGraph
- **LLM**: OpenAI GPT-4
- **Memory**: SQLite checkpointer
- **Architecture**: Multi-agent system

## Requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- npm o yarn
- uv (gestor de paquetes Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/escudo-escolar.git
cd escudo-escolar
```

### 2. Configurar Backend

```bash
cd backend

# Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

Configurar `.env`:
```env
DATABASE_URL=postgresql://usuario:password@host/database
SECRET_KEY=tu_clave_secreta_para_jwt
OPENAI_API_KEY=tu_api_key_de_openai
```

### 3. Configurar Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local
```

Configurar `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Configurar Base de Datos

```bash
cd ../backend

# Crear tablas (si usas los scripts SQL)
psql -U usuario -d database -f ../data/database/01_create_database.sql
psql -U usuario -d database -f ../data/database/02_create_user.sql
psql -U usuario -d database -f ../data/database/03_insert_demo_data.sql

# O crear usuarios de prueba
uv run python create_test_users.py
```

## Uso

### Iniciar Backend

```bash
cd backend
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

La API estará disponible en:
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Iniciar Frontend

```bash
cd frontend
npm run dev
```

La aplicación web estará disponible en:
- Frontend: http://localhost:3000

### Usuarios de Prueba

| Email | Contraseña | Rol |
|-------|-----------|-----|
| `gustavo.debasica@escudoescolar.demo` | `password123` | Administrador |
| `maripi.olet@escudoescolar.demo` | `password123` | Profesora |

## Estructura del Proyecto

```
escudo-escolar/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── core/           # Configuración y seguridad
│   │   ├── database/       # SQLAlchemy setup
│   │   ├── models/         # Modelos de base de datos
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── routes/         # Endpoints de la API
│   │   └── ml/             # Modelo de Machine Learning
│   ├── main.py             # Punto de entrada
│   └── README.md
├── frontend/               # Aplicación Next.js
│   ├── app/
│   │   ├── page.js         # Landing page
│   │   ├── login/          # Página de login
│   │   ├── panel/          # Dashboard principal
│   │   ├── chat/           # Chatbot
│   │   └── reportes/       # Formularios de reportes
│   ├── lib/
│   │   └── api.js          # Cliente API
│   └── README.md
├── chatbot/                # Sistema de chatbot
│   ├── app/
│   │   ├── agents/         # Agentes LangChain
│   │   ├── graph/          # LangGraph workflow
│   │   └── memory/         # Sistema de memoria
│   └── main.py
├── data/                   # Scripts y datos
│   └── database/           # Scripts SQL
├── docs/                   # Documentación
│   └── images/             # Capturas de pantalla
└── README.md               # Este archivo
```

## Flujo de Datos

```mermaid
sequenceDiagram
    participant P as Profesor
    participant F as Frontend
    participant A as API
    participant DB as Database
    participant ML as ML Model
    participant AI as OpenAI

    P->>F: Crear reporte estudiante
    F->>A: POST /reports/teacher
    A->>DB: Guardar reporte
    A->>DB: Verificar caso abierto
    alt No hay caso abierto
        A->>DB: Crear nuevo caso
    end
    A->>ML: Ejecutar predicción (background)
    ML->>DB: Obtener features históricos
    ML->>ML: Calcular probabilidad
    ML->>DB: Guardar predicción
    alt Probabilidad > umbral
        ML->>DB: Marcar como alerta
    end
    A->>F: Response exitoso
    F->>P: Mostrar confirmación

    P->>F: Ver dashboard
    F->>A: GET /dashboard/heatmap
    A->>DB: Obtener reportes + predicciones
    A->>F: Datos con alertas
    F->>P: Renderizar heatmap con alertas
```

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

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

## Agradecimientos

Este proyecto fue desarrollado como parte del bootcamp de The Bridge School. Agradecimientos especiales a:

- **Borja Barber** - Profesor del bootcamp de Data Science en The Bridge School, por su guía y apoyo durante el bootcamp.

- **Nicky Fariñez** - Profesor del bootcamp de Ciberseguridad en The Bridge School, por su guía y apoyo durante el bootcamp.

- **The Bridge School** - Por proporcionar la formación y recursos necesarios para el desarrollo de este proyecto.

---

<p align="center">
Desarrollado con dedicación para crear entornos escolares más seguros
</p>
