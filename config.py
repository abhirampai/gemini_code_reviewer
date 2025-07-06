from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GITHUB_APP_ID: str
    GITHUB_PRIVATE_KEY: str
    WEBHOOK_SECRET: str
    GEMINI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")
