from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = ""
    frontend_url: str = "http://localhost:3000"
    bootstrap_iterations: int = 10_000
    newey_west_threshold: float = 2.5
    default_regime_count: int = 3
    default_portfolio_size: int = 10
    fundamental_reporting_lag_days: int = 90
    data_quality_report_path: str = ""
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
