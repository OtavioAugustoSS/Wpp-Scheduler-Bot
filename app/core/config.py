from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Wpp-Scheduler-Bot"
    DEBUG: bool = True
    
    # API Keys (NVIDIA / OpenAI)
    NVIDIA_API_KEY: str
    OPENAI_BASE_URL: str = "https://integrate.api.nvidia.com/v1" # NVIDIA NIM default
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./bot.db"
    
    # WhatsApp
    WHATSAPP_VERIFY_TOKEN: str = "my_secure_verify_token"
    WHATSAPP_API_TOKEN: str = "placeholder_token"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
