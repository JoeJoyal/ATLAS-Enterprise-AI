from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration.

    Values are loaded from:
    1. Environment variables
    2. .evn file
    3. Default values defined below
    """

    # Load environment variables from the .env file.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket: str = ""

    # PostgreSQL Configuration
    database_url: str = ""

    # Amazon Bedrock Configuration
    bedrock_embed_model: str = "amazon.titan-embed-text-v2:0"
    bedrock_chat_model: str = "amazon.nova-lite-v1:0"
    embed_dim: int = 1024

    # File Upload Configuration
    max_upload_bytes: int = 10485760  # 10 MB

    # Pinecone Configuration
    pinecone_api_key: str = ""
    pinecone_index_name: str = "atlas-enterprice-ai-index"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    pinecone_ready_timeout: int = 180

    # RAG Configuration
    min_relevance: float = 0.25

    # HITL
    hitl_enabled: bool = True

    # Conversation Memory Configuration
    memory_turns: int = 6


@lru_cache
def settings() -> Settings:
    """
    Create Settings only once and reuse the same instance.
    """
    return Settings()