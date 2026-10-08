from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ============================================================
# APPLICATION SETTINGS
# ============================================================

class Settings(BaseSettings):

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    APP_NAME: str = "Universal Workspace"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    API_V1_PREFIX: str = "/api/v1"

    # --------------------------------------------------------
    # Storage
    # --------------------------------------------------------

    STORAGE_PATH: str = "../storage"

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    DATABASE_URL: str

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --------------------------------------------------------
    # OpenAI
    # --------------------------------------------------------

    OPENAI_API_KEY: str | None = None

    # --------------------------------------------------------
    # Pydantic Settings Configuration
    # --------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========================================================
    # STORAGE DIRECTORY
    # ========================================================

    @property
    def storage_dir(self) -> Path:

        storage_path = Path(self.STORAGE_PATH)

        if not storage_path.is_absolute():

            storage_path = BASE_DIR / storage_path

        return storage_path.resolve()


# ============================================================
# SETTINGS INSTANCE
# ============================================================

settings = Settings()


# ============================================================
# CREATE STORAGE DIRECTORY
# ============================================================

settings.storage_dir.mkdir(
    parents=True,
    exist_ok=True,
)