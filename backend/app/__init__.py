from flask import Flask
from flask_cors import CORS
from config import Config
from neo4j import GraphDatabase

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Initialize Neo4j driver
    app.neo4j_driver = GraphDatabase.driver(
        Config.NEO4J_URI,
        auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
    )
    
    # Register blueprints
    from app.routes.recommendations import recommendations_bp
    app.register_blueprint(recommendations_bp)
    
    return app