"""
Configuración de la aplicación usando Pydantic Settings
Carga automáticamente las variables de entorno desde .env
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuración global de la aplicación"""

    # Información de la aplicación
    APP_NAME: str = "Escudo Escolar"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # Base de datos PostgreSQL
    DATABASE_URL: str

    # Seguridad y autenticación JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS - Orígenes permitidos
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # OpenAI (opcional, para el chatbot)
    OPENAI_API_KEY: str | None = None

    # Machine Learning - Ruta al modelo entrenado
    MODEL_PATH: str = "./models/bullying_detection_model.json"

    @property
    def origins_list(self) -> List[str]:
        """Convierte la cadena de orígenes en una lista"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()
