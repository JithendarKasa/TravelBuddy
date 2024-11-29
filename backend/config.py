from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    NEO4J_URI = "neo4j://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "Travel@123"
    