from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # настройка pydantic для загрузки переменных из .env файла
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_expire_minutes: int


# создаём объект настроек который автоматически подтянет значения из .env
settings = Settings()
