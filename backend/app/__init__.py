from flask import Flask
from flask_cors import CORS
from neo4j import GraphDatabase
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Initialize Neo4j driver
    try:
        app.neo4j_driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )
        logger.info("Successfully connected to Neo4j database")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {str(e)}")
        raise
    
    # Register blueprints
    from app.routes.recommendations import recommendations_bp
    app.register_blueprint(recommendations_bp)
    
    # Test route
    @app.route('/api/health')
    def health_check():
        return {"status": "healthy", "service": "TravelBuddy API"}
    
    return app