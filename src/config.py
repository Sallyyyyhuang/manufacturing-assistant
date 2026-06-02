from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    model_name: str = "claude-sonnet-4-20250514"

    model_config = {"env_file": ".env"}


settings = Settings()
