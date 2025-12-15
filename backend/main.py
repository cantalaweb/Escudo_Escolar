"""
Escudo Escolar - Backend API
Sistema de detección temprana de bullying escolar

Punto de entrada principal de la aplicación FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import health, auth, chat, reports, coordinator

# ==============================================================================
# INICIALIZACIÓN DE LA APLICACIÓN
# ==============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de detección temprana de bullying escolar con IA",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# ==============================================================================
# CONFIGURACIÓN DE CORS
# ==============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# REGISTRO DE ROUTERS
# ==============================================================================

# Health check (sin prefijo, en raíz)
app.include_router(health.router, prefix="/api")

# Autenticación
app.include_router(auth.router)

# Chatbot
app.include_router(chat.router)

# Reportes
app.include_router(reports.router)

# Coordinación
app.include_router(coordinator.router)


# ==============================================================================
# ENDPOINT RAÍZ
# ==============================================================================

@app.get("/")
def root():
    """Endpoint raíz con información del API"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ==============================================================================
# EJECUCIÓN EN DESARROLLO
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
