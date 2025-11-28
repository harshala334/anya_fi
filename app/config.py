import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Anya.fi - Shopping Guardian"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost/anya_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_session_ttl: int = 3600  # 1 hour
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_webhook_url: Optional[str] = None
    telegram_webhook_secret: Optional[str] = None
    
    # WhatsApp Business API
    whatsapp_access_token: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_business_account_id: Optional[str] = None
    whatsapp_verify_token: Optional[str] = "anya_verify_token_2024"
    whatsapp_webhook_url: Optional[str] = None
    
    # Groq (NEW)
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-8b-instant"

    # (OPTIONAL) OpenAI fields left for compatibility
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Account Aggregator
    aa_enabled: bool = False
    aa_base_url: Optional[str] = None
    aa_client_id: Optional[str] = None
    aa_client_secret: Optional[str] = None
    aa_fiu_id: Optional[str] = None
    
    # Financial Logic
    comfort_zone_threshold: float = 0.5  # 50% of saving goal
    
    def validate_required_settings(self):
        """Validate that required settings are present."""
        errors = []

        if not self.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is required")

        # now Groq is mandatory instead of OpenAI
        if not self.groq_api_key:
            errors.append("GROQ_API_KEY is required")

        if errors:
            raise ValueError(f"Missing required settings: {', '.join(errors)}")
    
    @property
    def is_production(self) -> bool:
        return not self.debug


# Global settings instance
settings = Settings()

try:
    settings.validate_required_settings()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
    print("Some features may not work correctly.")
