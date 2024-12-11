from flask import Flask, jsonify, request
from flask_cors import CORS  # To handle CORS issues
from travelsearch import TravelBuddyQueries

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/api/hotels/search', methods=['GET'])
def search_hotels():
    try:
        # Get search parameters
        features = request.args.getlist('features')
        search_text = request.args.get('search_text', '')
        limit = int(request.args.get('limit', 10))

        print(f"Search text: {search_text}")  # Debug log
        print(f"Features: {features}")  # Debug log

        # Initialize search
        hotel_search = TravelBuddyQueries()
        
        try:
            # Get search results
            results = hotel_search.search_hotels(
                search_text=search_text,
                features=features,
                limit=limit
            )

            return jsonify({
                "status": "success",
                "results": results
            })
            
        finally:
            hotel_search.close()

    except Exception as e:
        print(f"Error in search endpoint: {str(e)}")  # Debug log
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/hotels/features', methods=['GET'])
def get_features():
    return jsonify({
        "status": "success",
        "features": [
            "family-friendly",
            "business",
            "luxury",
            "beach",
            "city center",
            "romantic",
            "spa",
            "budget"
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
