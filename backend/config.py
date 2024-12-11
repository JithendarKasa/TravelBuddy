import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Neo4j Configuration
    NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'Travel@123')  # Replace with your password

    # Flask Configuration
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

    # API Configuration
    API_PREFIX = '/api'
    DEFAULT_RESULTS_LIMIT = 10
    MIN_REVIEW_COUNT = 5
    MIN_RATING_THRESHOLD = 7.0

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')