from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
from pydantic import model_validator


class Settings(BaseSettings):
    #database
    database_url: Optional[str] = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "to be changed..."
    postgres_db: str = "flood_predictor"

    api_port: int = 8000
    secret_key: str = "to be changed..."
    cors_origins: List[str] = ["*"]

    usgs_api_base_url: str = "https://waterservices.usgs.gov/nwis/iv"
    noaa_api_base_url: str = "https://api.weather.gov"
    noaa_api_token: str = "to be changed..."


    #Application 
    log_level: str = "INFO"
    data_refresh_interval: int = 300

    class Config:
        env_file = (".env", "../.env")
        case_sensitive = False
    
    @model_validator(mode='after')
    def compute_database_url(self):
        if not self.database_url:
            self.database_url = f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        return self

@lru_cache
def get_settings():
    return Settings()

settings: Settings = get_settings()