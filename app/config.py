# app/config.py
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api")
API_VERSION = "v1"
