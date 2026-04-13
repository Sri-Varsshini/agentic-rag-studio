from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    openai_api_key: str
    langsmith_api_key: str = ""
    langsmith_project: str = "agentic-rag-masterclass"
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    supabase_storage_bucket: str = "documents"
    reranker_enabled: bool = False
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"
    search_api_key: str = ""
    search_provider: str = "tavily"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
