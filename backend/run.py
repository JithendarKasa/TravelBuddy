from app import create_app
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    try:
        logger.info("Starting TravelBuddy API server...")
        app.run(debug=True, port=5000)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")