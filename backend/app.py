from flask import Flask, jsonify, request
from flask_cors import CORS  # To handle CORS issues
from travelsearch import TravelBuddyQueries

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/hotels/search', methods=['GET'])
def search_hotels():
    try:
        # Get search parameters from query string
        features = request.args.getlist('features')  # Handle multiple features
        search_text = request.args.get('search_text', '')
        limit = int(request.args.get('limit', 10))

        # Initialize database connection
        queries = TravelBuddyQueries()
        
        try:
            # Get search results
            hotels = queries.search_hotels_by_features(features, limit)
            
            # Format the response
            formatted_hotels = []
            for hotel in hotels:
                formatted_hotel = {
                    "name": hotel["Hotel_Name"],
                    "location": hotel["Hotel_Address"],
                    "rating": hotel["Average_Score"],
                    "reviewCount": hotel["review_count"],
                    "averageReviewScore": round(hotel["avg_reviewer_score"], 1) if hotel["avg_reviewer_score"] else 0,
                    "highlights": [],
                    "considerations": []
                }
                
                # Add highlights based on reviews
                if formatted_hotel["averageReviewScore"] >= 8:
                    formatted_hotel["highlights"].append("Highly rated")
                if "breakfast" in str(hotel.get("Tags", "")).lower():
                    formatted_hotel["highlights"].append("Great breakfast!")
                if "location" in str(hotel.get("Tags", "")).lower():
                    formatted_hotel["highlights"].append("Excellent location")
                    
                formatted_hotels.append(formatted_hotel)

            return jsonify({
                "status": "success",
                "results": formatted_hotels
            })
            
        finally:
            queries.close()

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/api/hotels/features', methods=['GET'])
def get_features():
    """Get available search features/tags"""
    try:
        queries = TravelBuddyQueries()
        try:
            # Get distinct tags from the database
            common_features = [
                "family-friendly",
                "business",
                "luxury",
                "beach",
                "city center",
                "romantic",
                "spa",
                "budget"
            ]
            return jsonify({
                "status": "success",
                "features": common_features
            })
        finally:
            queries.close()
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)