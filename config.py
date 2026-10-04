import os

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)

DATABASE = os.getenv(
    "DATABASE",
    "database/stylemantra.db"
)

UPLOAD_FOLDER = os.getenv(
    "UPLOAD_FOLDER",
    "static/uploads"
)