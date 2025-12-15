"""
Endpoints del chatbot de apoyo
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])


# Mock del grafo de agentes (será reemplazado por LangGraph/OpenAI)
class MockGraph:
    def invoke(self, inputs):
        mensaje = inputs.get('mensaje_entrada', '')
        return {
            'respuesta_final': f"[MOCK] Procesando tu mensaje: '{mensaje}'. "
                              "Recuerda que no estás solo. ¿Quieres contarme más?"
        }


app_graph = MockGraph()


class ChatRequest(BaseModel):
    mensaje: str


class ChatResponse(BaseModel):
    respuesta: str


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Endpoint del chatbot de apoyo emocional

    Args:
        request: Mensaje del estudiante

    Returns:
        Respuesta del chatbot

    Note:
        Actualmente es un mock. Será reemplazado por LangGraph con OpenAI
    """
    inputs = {"mensaje_entrada": request.mensaje}
    resultado = app_graph.invoke(inputs)

    return {"respuesta": resultado['respuesta_final']}
