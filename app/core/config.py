import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Laptop Price Predictor API"
    API_V1_STR: str = "/api/v1"
    
    # Security config
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretjwtkeyforlaptoppricepredictionapi123!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # API key security
    API_KEY_NAME: str = "access_token_key"
    API_KEY: str = os.getenv("API_KEY", "lappredict_secure_api_key_2026")
    
    # Redis configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # MongoDB configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "laptop_price_db")
    
    # Model configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "app/models/pipe.pkl")
    DF_PATH: str = os.getenv("DF_PATH", "app/models/df.pkl")

settings = Settings()
