from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    #database
    database_url: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "to be changed..."
    postgres_db: str = "flood_predictor"

    api_port: int = 8000
    secret_key: str = "to be changed..."

    usgs_api_base_url: str = "https://waterservices.usgs.gov/nwis/iv"
    noaa_api_base_url: str = "https://api.weather.gov"
    noaa_api_token: str = "to be changed..."


    #Application 
    log_level: str = "INFO"
    data_refresh_interval: int = 300

    class Config:
        env_file = (".env", "../.env")
        case_sensitive = False
    
@lru_cache
def get_settings():
    return Settings()

settings: Settings = get_settings()