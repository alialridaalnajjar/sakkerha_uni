import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ─── Flask ───────────────────────────────────────────
    SECRET_KEY  = os.getenv("SECRET_KEY", "fallback-secret")
    DEBUG       = os.getenv("FLASK_DEBUG", "0") == "1"

    # ─── Database ────────────────────────────────────────
    DATABASE_URL = os.getenv("DATABASE_URL")

    # ─── Gemini ──────────────────────────────────────────
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # ─── Firebase ────────────────────────────────────────
    FIREBASE_API_KEY      = os.getenv("FIREBASE_API_KEY")
    FIREBASE_PROJECT_ID   = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_STORAGE_BUCKET  = os.getenv("FIREBASE_STORAGE_BUCKET")
    FIREBASE_DATABASE_URL    = os.getenv("FIREBASE_DATABASE_URL")
    FIREBASE_AUTH_DOMAIN     = os.getenv("FIREBASE_AUTH_DOMAIN")

    # ─── Email ───────────────────────────────────────────
    MAIL_SERVER         = "smtp.gmail.com"
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USERNAME        = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD        = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER  = os.getenv("MAIL_DEFAULT_SENDER")