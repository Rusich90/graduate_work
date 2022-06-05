from pydantic import BaseSettings
from pydantic import SecretStr


class DatabaseSettings(BaseSettings):
    engine: str
    host: str
    port: int
    db: str
    password: SecretStr
    user: str

    class Config:
        env_prefix = "POSTGRES_"

    def db_url(self):
        return f'{self.engine}://{self.user}:{self.password.get_secret_value()}@{self.host}/{self.db}'


class CacheSettings(BaseSettings):
    host: str
    port: int
    expire_time: int

    class Config:
        env_prefix = "REDIS_"


class SchedulerSettings(BaseSettings):
    jobstore: CacheSettings = CacheSettings()
    subscribe_hour: str
    subscribe_minute: str
    pending_hour: str
    pending_minute: str

    class Config:
        env_prefix = "SCHEDULER_"


class JWTSettings(BaseSettings):
    algorithm: str
    secret_key: SecretStr

    class Config:
        env_prefix = "JWT_"


class LoggingSettings(BaseSettings):
    level: str

    class Config:
        env_prefix = "LOG_"


class BillingSettings(BaseSettings):
    id: int
    token: SecretStr
    url: str
    refund_url: str
    redirect_url: str

    class Config:
        env_prefix = "BILLING_"
