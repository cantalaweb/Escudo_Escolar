"""
Escudo Escolar - Backend API
Sistema de detección temprana de bullying escolar

Punto de entrada principal de la aplicación FastAPI
"""

import os
import logging
import hashlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import health, auth, chat, reports, coordinator, dashboard, chatbot
from app.ml.predictor import MODEL_PATH, cargar_modelo, OPTIMAL_THRESHOLD
from app.ml.model_integrity import MODEL_SHA256, OPTIMAL_THRESHOLD as EXPECTED_THRESHOLD

logger = logging.getLogger(__name__)

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
# VALIDACIÓN DE MODELO ML AL INICIO
# ==============================================================================

def calculate_file_sha256(filepath: str) -> str:
    """Calcula el SHA-256 de un archivo"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@app.on_event("startup")
async def validate_ml_model():
    """
    Valida que el modelo ML existe, tiene la integridad correcta y se puede cargar.
    Verificaciones de seguridad:
    1. Existencia del archivo
    2. Hash SHA-256 (integridad)
    3. Umbral correcto
    4. Carga exitosa del modelo
    """
    logger.info("=" * 60)
    logger.info("VALIDANDO MODELO DE MACHINE LEARNING")
    logger.info("=" * 60)

    # 1. Verificar que el archivo existe
    if not os.path.exists(MODEL_PATH):
        error_msg = f"""
╔══════════════════════════════════════════════════════════════╗
║  ERROR CRÍTICO: MODELO ML NO ENCONTRADO                      ║
╚══════════════════════════════════════════════════════════════╝

El servidor NO puede iniciarse sin el modelo de Machine Learning.

Ruta esperada: {MODEL_PATH}

SOLUCIÓN:
1. Asegúrate de que el modelo existe en la ruta especificada
2. Si no tienes el modelo, entrenalo usando:
   python data/src/train_model.py

El servidor se detendrá ahora.
        """
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    # 2. Verificar integridad del modelo (SHA-256)
    logger.info("Verificando integridad del modelo (SHA-256)...")
    try:
        actual_hash = calculate_file_sha256(MODEL_PATH)

        if actual_hash != MODEL_SHA256:
            # ALERTA DE SEGURIDAD: Hash no coincide
            error_msg = f"""
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  ALERTA DE SEGURIDAD: MODELO MODIFICADO                  ║
╚══════════════════════════════════════════════════════════════╝

El hash SHA-256 del modelo NO coincide con el valor esperado.
Esto indica que el archivo ha sido modificado, corrupto o reemplazado.

Ruta del modelo: {MODEL_PATH}

Hash esperado: {MODEL_SHA256}
Hash actual:   {actual_hash}

POSIBLES CAUSAS:
1. El modelo fue modificado por un atacante
2. El archivo está corrupto
3. Se reentrenó el modelo sin actualizar model_integrity.py

SOLUCIÓN:
1. Si reentrenaste el modelo:
   - Actualiza MODEL_SHA256 en app/ml/model_integrity.py
   - Usa: shasum -a 256 {MODEL_PATH}

2. Si NO reentrenaste el modelo:
   - ⚠️ POSIBLE ATAQUE - Investiga inmediatamente
   - Restaura el modelo original desde backup
   - Revisa logs de acceso al servidor

El servidor se detendrá ahora por seguridad.
            """
            logger.critical(error_msg)
            logger.critical(f"INTENTO DE CARGA CON HASH INCORRECTO - Modelo: {MODEL_PATH}")
            logger.critical(f"Hash esperado: {MODEL_SHA256}")
            logger.critical(f"Hash detectado: {actual_hash}")
            raise SecurityError(error_msg)

        logger.info(f"✓ Hash SHA-256 verificado: {actual_hash[:16]}...")

    except SecurityError:
        raise
    except Exception as e:
        error_msg = f"Error calculando hash del modelo: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # 3. Verificar que el umbral coincide
    if OPTIMAL_THRESHOLD != EXPECTED_THRESHOLD:
        error_msg = f"""
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  ALERTA: UMBRAL MODIFICADO                               ║
╚══════════════════════════════════════════════════════════════╝

El umbral en predictor.py ({OPTIMAL_THRESHOLD}) no coincide con el
umbral esperado en model_integrity.py ({EXPECTED_THRESHOLD}).

Esto puede indicar modificación del código o desincronización.

SOLUCIÓN:
Asegúrate de que ambos valores coincidan:
- app/ml/predictor.py: OPTIMAL_THRESHOLD
- app/ml/model_integrity.py: OPTIMAL_THRESHOLD

El servidor se detendrá ahora.
        """
        logger.critical(error_msg)
        logger.critical(f"UMBRAL INCORRECTO - Esperado: {EXPECTED_THRESHOLD}, Actual: {OPTIMAL_THRESHOLD}")
        raise ValueError(error_msg)

    logger.info(f"✓ Umbral validado: {OPTIMAL_THRESHOLD}")

    # 4. Intentar cargar el modelo para verificar que es válido
    try:
        logger.info(f"Cargando modelo desde: {MODEL_PATH}")
        modelo = cargar_modelo()

        if modelo is None:
            raise ValueError("El modelo se cargó pero retornó None")

        logger.info("✓ Modelo ML cargado exitosamente")
        logger.info(f"✓ Tipo de modelo: XGBoost Classifier")
        logger.info("=" * 60)
        logger.info("VALIDACIÓN COMPLETA - Modelo listo para uso")
        logger.info("=" * 60)

    except Exception as e:
        error_msg = f"""
╔══════════════════════════════════════════════════════════════╗
║  ERROR CRÍTICO: MODELO ML CORRUPTO O INVÁLIDO               ║
╚══════════════════════════════════════════════════════════════╝

El modelo existe y tiene el hash correcto, pero no se puede cargar.

Ruta: {MODEL_PATH}
Error: {str(e)}

SOLUCIÓN:
1. Reentrena el modelo usando: python data/src/train_model.py
2. Actualiza el hash en model_integrity.py

El servidor se detendrá ahora.
        """
        logger.error(error_msg)
        raise RuntimeError(error_msg)


class SecurityError(Exception):
    """Excepción personalizada para errores de seguridad"""
    pass

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

# Dashboard
app.include_router(dashboard.router)

# Chatbot (multi-agent support system)
app.include_router(chatbot.router)


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
