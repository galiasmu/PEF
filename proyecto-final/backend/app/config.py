"""Configuración centralizada del analizador.

Las variables se leen una sola vez desde el entorno (o desde ``backend/.env``)
y quedan disponibles en el objeto ``settings``. El resto de los módulos
importa ``settings`` en lugar de leer ``os.environ`` por su cuenta, así hay
un único lugar con los valores por defecto.
"""
import os

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

load_dotenv()

DEFAULT_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"


class Settings(BaseModel):
    """Parámetros de ejecución, con sus valores por defecto."""

    # Permite el campo "model_name" (pydantic reserva el prefijo "model_").
    model_config = ConfigDict(protected_namespaces=())

    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "").strip()
    target_type: str = os.getenv("TARGET_TYPE", "video").strip()  # "video" | "channel"
    target_id: str = os.getenv("TARGET_ID", "").strip()
    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL", "5"))
    window_seconds: int = int(os.getenv("WINDOW_SECONDS", "10"))
    max_queue: int = int(os.getenv("MAX_QUEUE", "5000"))
    model_name: str = os.getenv("SENTIMENT_MODEL", DEFAULT_MODEL).strip()

    def require_youtube(self) -> None:
        """Verifica que esté la configuración mínima para consultar YouTube.

        Raises:
            RuntimeError: si falta la API key o el ID del video/canal.
        """
        if not self.youtube_api_key or not self.target_id:
            raise RuntimeError("Falta YOUTUBE_API_KEY o TARGET_ID en backend/.env")


settings = Settings()
