import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus einer .env-Datei
load_dotenv()

class Settings:
    """Hält die globalen Konfigurationseinstellungen für die Anwendung."""
    
    APP_NAME: str = "FastAPI Chess Server"
    APP_VERSION: str = "1.0.0"
    
    # CORS-Einstellungen
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")  # z. B. "http://localhost,http://example.com"
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS = ["*"]
    ALLOW_HEADERS = ["*"]

    # Server-Einstellungen
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"

    # Weitere Einstellungen (z. B. Datenbank, API-Keys) können hier hinzugefügt werden.

settings = Settings()
