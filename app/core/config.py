from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentiric Knowledge Service"
    API_V1_STR: str = "/api/v1"
    ENV: str = "production"
    LOG_LEVEL: str = "INFO"
    
    POSTGRES_URL: str
    
    VECTOR_DB_HOST:  str = "qdrant"
    VECTOR_DB_PORT: int = 6333
    VECTOR_DB_COLLECTION_NAME: str = "sentiric_kb"
    VECTOR_DB_COLLECTION_PREFIX: str = "sentiric_kb_"
    VECTOR_DB_EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()