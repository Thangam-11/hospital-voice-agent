from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ==========================
    # Application
    # ==========================
    app_name: str = "Hospital AI Voice Agent"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

   # twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: int

    # ==========================
    # LLM
    # ==========================

    openrouter_api_key: str
    llm_model: str = "qwen/qwen3-30b-a3b-instruct-2507"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    

    # ==========================
    # Embeddings
    # ==========================
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    embedding_dim: int = 768

    # ==========================
    # Qdrant
    # ==========================
    

    # ==========================
    # PostgreSQL
    # ==========================
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    database_url: str

    # ==========================
    # Redis
    # ==========================
    redis_url: str
    redis_cache_enabled: bool = True
    redis_cache_ttl_seconds: int = 3600

    # ==========================
    # Voice
    # ==========================

    deepgram_api_key: str
    elevenlabs_api_key: str

    # ==========================
    # Monitoring
    # ==========================
    langsmith_enabled: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "hospital-voice-agent"

    prometheus_port: int = 9090

    # ==========================
    # Security
    # ==========================
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # ==========================
    # Feature Flags
    # ==========================
    rag_enabled: bool = True
    pii_guardrail_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()