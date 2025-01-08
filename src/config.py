from typing import ClassVar
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class Configs(BaseSettings):
    # General settings
    ENV: str = os.getenv("ENV", "Local")

    # Server configurations
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Application instance configurations
    NAMESPACE: str = "IHCE.Engage"
    PIPELINE: str = "IdentityManagement.Service"
    PIPELINE_CODE: str = ""  # Assign this value as needed
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "Handles identity and access management services."
    PROJECT_OWNER: str = "FearlessFalcons"
    CONTACT_EMAIL: str = "hubs.infinity@gmail.com"

    # Application identifier using formatted string
    APP_IDENTIFIER: str = f"[Instance -- {NAMESPACE}:{PIPELINE}] [Pipeline Owner -- {PROJECT_OWNER}] [Version -- {PROJECT_VERSION}]"

    # Microservices API configurations
    API_PREFIX: str = "/api"
    API_DOC_URL: str = "/swagger/index.html"

    PROJECT_ROOT: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # Date and time formats
    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"

    # Authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    #Redis Connector
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis-11916.c14.us-east-1-3.ec2.redns.redis-cloud.com")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "11916")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "FIqJ3HuO4zL3kJr0uCZfAeSqsklNZcFC")
    REDIS_USERNAME: str = os.getenv("REDIS_USERNAME", "default")

    # Authentication settings
    HMAC_SECRET_KEY: str = os.getenv("HMAC_SECRET_KEY", "TheInvincible_rANVAN2dot0")
    HMAC_TOKEN_EXPIRATION_SECONDS: int = 24 * 60 * 60  # 86,400 seconds i.e 1 day

    # Database settings
    # DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_HOST: str = os.getenv("DB_HOST", "5.223.48.13")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD","root77Dot0#1125")
    # DB_PASSWORD: str = os.getenv("DB_PASSWORD","_root77")
    DB_NAME: str = os.getenv("DB_NAME", "dbIHCEIdentity")
    DB_DIALECT: str = os.getenv("DB_DIALECT", "postgresql")

    # Database URI
    DB_CONTEXT: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}"

    # Dynamically generate DB_CONNECTION_STRING using the DB_CONTEXT format
    DB_CONNECTION_STRING: str = DB_CONTEXT.format(
        db_engine=DB_DIALECT,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )

    SSO_MFA_URL: str = os.getenv("SSO_MFA_URL","https://onboarding.infinityhubs.in")

    # SMTP settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "infinityhubs.in")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.zeptomail.in")
    SMTP_PORT: int = os.getenv("SMTP_PORT", 587)
    SMTP_USER: str = os.getenv("SMTP_USER", "emailapikey")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "PHtE6r1eQe6+iDQr8xRU7KTrQpT1MIx6+u5jKlNOsd1LX6QFTE1drd0swWezo0sqUaFDQf+Zndpqt7PJseyDcW7oMm9OWWqyqK3sx/VYSPOZsbq6x00Zt1odf0zaU4Drc9du3CzQu9nYNA==")

    # Query settings
    PAGE: ClassVar[int] = 1
    PAGE_SIZE: int = 20
    ORDERING: str = "-id"

    # Pydantic settings
    class Config:
        case_sensitive = True


# Create an instance of the Configs class to access settings
AppConfigs = Configs()

