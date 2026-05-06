from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "notifications_db"

    rabbitmq_uri: str = "amqp://guest:guest@localhost:5672/"
    
    rabbitmq_onboarding_exchange: str = "onboarding.exchange"
    rabbitmq_offboarding_exchange: str = "offboarding.exchange"
    
    rabbitmq_onboarding_queue: str = "notification.onboarding.queue"

    # rabbitmq_offboarding_queue: str = "notification.offboarding.queue"

    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")


settings = Settings()
