"""
Router para el chatbot de apoyo emocional
Sistema multi-agente con RAG para víctimas de bullying
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from app.chatbot.graph import app_graph
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["chatbot"]
)


class ChatRequest(BaseModel):
    """
    Request body para el endpoint de chat
    """
    message: str = Field(..., description="Mensaje del usuario", min_length=1)
    thread_id: str = Field(..., description="ID de sesión para mantener el historial", min_length=1)


class ChatResponse(BaseModel):
    """
    Response body del chatbot
    """
    respuesta: str = Field(..., description="Respuesta generada por Alex (el chatbot)")
    thread_id: str = Field(..., description="ID de sesión devuelto")


@router.post("/chatbot", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal del chatbot de apoyo emocional.

    Sistema multi-agente que:
    1. Perfila al usuario (víctima, agresor, observador, etc.)
    2. Busca información relevante en la base de datos (RAG)
    3. Genera una respuesta empática y adaptada

    **No requiere autenticación** - Diseñado para máxima accesibilidad.
    **No almacena conversaciones** - Máxima privacidad (solo en memoria).
    """
    try:
        # Configurar la sesión con el thread_id
        config = {"configurable": {"thread_id": request.thread_id}}

        # Crear mensaje del usuario
        mensaje_nuevo = HumanMessage(content=request.message)

        # Ejecutar el grafo multi-agente
        logger.info(f"Procesando mensaje del chat (thread: {request.thread_id[:8]}...)")
        resultado = app_graph.invoke({"mensajes": [mensaje_nuevo]}, config=config)

        # Extraer respuesta final
        respuesta_final = resultado.get('respuesta_final', '')

        if not respuesta_final:
            raise ValueError("El chatbot no generó una respuesta válida")

        return ChatResponse(
            respuesta=respuesta_final,
            thread_id=request.thread_id
        )

    except Exception as e:
        logger.error(f"Error en chatbot: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el mensaje: {str(e)}"
        )


@router.get("/chatbot/health")
async def chatbot_health():
    """
    Health check específico del chatbot.
    Verifica que el sistema multi-agente esté disponible.
    """
    try:
        # Verificar que el grafo está compilado
        if app_graph is None:
            raise ValueError("Grafo del chatbot no inicializado")

        return {
            "status": "online",
            "service": "chatbot",
            "agents": ["profiler", "query_generator", "responder"],
            "rag": "chroma_db"
        }
    except Exception as e:
        logger.error(f"Health check del chatbot falló: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Chatbot no disponible: {str(e)}"
        )
