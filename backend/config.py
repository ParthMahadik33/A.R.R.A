import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_DIR = os.path.join(BASE_DIR, 'db')

# Database Config
DB_PATH = os.path.join(DB_DIR, 'arra.db')
DATABASE_URI = f"sqlite:///{DB_PATH}"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Corridor boundaries (Howrah-Chennai Main Line)
HOWRAH_COORDS = {"lat": 22.5834, "lng": 88.3411}
CHENNAI_COORDS = {"lat": 13.0827, "lng": 80.2707}

# Safety thresholds (in minutes)
COLLISION_CRITICAL_MIN = 3.0    # Emergency braking issued automatically
COLLISION_WARNING_MIN = 8.0     # Alert and caution signal issued

# Speed parameters (km/h) for trains in simulation
MAX_TRAIN_SPEED = 110
DEFAULT_TRAIN_SPEED = 80

# Web server settings
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5000))
DEBUG = False
