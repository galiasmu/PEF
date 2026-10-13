import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL", 5))
    window_seconds: int = int(os.getenv("WINDOW_SECONDS", 10))
    max_queue: int = int(os.getenv("MAX_QUEUE", 5000))
    model_name: str = os.getenv("SENTIMENT_MODEL", "cardiffnlp/twitter-xlm-roberta-base-sentiment")
    target_type: str = os.getenv("TARGET_TYPE", "video")  # "video" | "channel"
    target_id: str = os.getenv("TARGET_ID", "")

settings = Settings()
