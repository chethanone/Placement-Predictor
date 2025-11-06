# Firebase Configuration for Placement Predictor
# Install: pip install firebase-admin
import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
}

# Service Account Path (Download from Firebase Console)
FIREBASE_CREDENTIALS_PATH = "config/firebase-credentials.json"

# Collections
COLLECTIONS = {
    'students': 'students',
    'teachers': 'teachers',
    'assessments': 'assessments',
    'quiz_results': 'quiz_results',
    'skill_scores': 'skill_scores',
}
