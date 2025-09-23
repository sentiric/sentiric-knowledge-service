# sentiric-knowledge-service/app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """
    Uygulamanın tüm yapılandırmasını ortam değişkenlerinden ve .env dosyasından
    yöneten merkezi sınıf.
    """
    # Proje Meta Verileri
    PROJECT_NAME: str = "Sentiric Knowledge Service"
    API_V1_STR: str = "/api/v1"

    # Ortam Ayarları
    ENV: str = Field("production", validation_alias="ENV")
    LOG_LEVEL: str = Field("INFO", validation_alias="LOG_LEVEL")

    # Gözlemlenebilirlik Alanları
    SERVICE_VERSION: str = Field("0.0.0", validation_alias="SERVICE_VERSION")
    GIT_COMMIT: str = Field("unknown", validation_alias="GIT_COMMIT")
    BUILD_DATE: str = Field("unknown", validation_alias="BUILD_DATE")

    # Veritabanı Bağlantıları
    POSTGRES_URL: str = Field(validation_alias="POSTGRES_URL")
    VECTOR_DB_HOST: str = Field("qdrant", validation_alias="QDRANT_HOST")
    VECTOR_DB_HTTP_PORT: int = Field(6333, validation_alias="QDRANT_HTTP_PORT")
    
    QDRANT_API_KEY: Optional[str] = Field(None, validation_alias="QDRANT_API_KEY")
    
    # RAG Modeli Ayarları
    EMBEDDING_MODEL_NAME: str = Field("all-MiniLM-L6-v2", validation_alias="QDRANT_DB_EMBEDDING_MODEL_NAME")
    VECTOR_DB_COLLECTION_PREFIX: str = "sentiric_kb_"

    # API Sunucusu Ayarları
    KNOWLEDGE_SERVICE_HTTP_PORT: int = Field(12040, validation_alias="KNOWLEDGE_SERVICE_HTTP_PORT")
    KNOWLEDGE_SERVICE_GRPC_PORT: int = Field(12041, validation_alias="KNOWLEDGE_SERVICE_GRPC_PORT")

    # --- YENİ: mTLS Sertifika Yolları ---
    KNOWLEDGE_SERVICE_CERT_PATH: str = Field(validation_alias="KNOWLEDGE_SERVICE_CERT_PATH")
    KNOWLEDGE_SERVICE_KEY_PATH: str = Field(validation_alias="KNOWLEDGE_SERVICE_KEY_PATH")
    GRPC_TLS_CA_PATH: str = Field(validation_alias="GRPC_TLS_CA_PATH")
    # --- DEĞİŞİKLİK SONU ---
    
    # Pydantic'e .env dosyasını okumasını ve büyük/küçük harf duyarsız olmasını söyler
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore', case_sensitive=False)

settings = Settings()