from pydantic import BaseSettings, SecretStr


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

    class Config:
        env_prefix = "BILLING_"