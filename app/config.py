from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    app_name: str = "Security Log Analyzer"
    debug: bool = True
    database_url: str = f"sqlite:///{BASE_DIR / 'security_logs.db'}"
    upload_dir: Path = BASE_DIR / "data" / "uploaded"
    report_dir: Path = BASE_DIR / "reports" / "generated"


settings = Settings()
