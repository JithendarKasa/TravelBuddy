from flask import Flask, jsonify, request
from flask_cors import CORS
from travelsearch import TravelBuddyQueries
from destination_graph import DestinationGraphManager

app = Flask(__name__)
CORS(app)

# Initialize Neo4j connection
graph_manager = DestinationGraphManager(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="moderndbproject",
    database="travelbuddy"
)

@app.route('/api/hotels/search', methods=['GET'])
def search_hotels():
    try:
        features = request.args.getlist('features')
        search_text = request.args.get('search_text', '')
        limit = int(request.args.get('limit', 10))

        print(f"Search text: {search_text}")
        print(f"Features: {features}")

        hotel_search = TravelBuddyQueries()
        try:
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
        print(f"Error in search endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/destinations/related', methods=['GET'])
def get_related_destinations():
    try:
        city = request.args.get('city')
        tag_type = request.args.get('tag_type')
        limit = int(request.args.get('limit', 5))

        if not city:
            return jsonify({
                "status": "error",
                "message": "City parameter is required"
            }), 400

        results = graph_manager.find_related_destinations(
            city=city,
            tag_type=tag_type,
            limit=limit
        )

        return jsonify({
            "status": "success",
            "results": results
        })

    except Exception as e:
        print(f"Error in related destinations endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/destinations/hotels', methods=['GET'])
def get_connected_hotels():
    try:
        city = request.args.get('city')
        tags = request.args.getlist('tags')
        min_rating = float(request.args.get('min_rating', 4.0))
        limit = int(request.args.get('limit', 10))

        if not city:
            return jsonify({
                "status": "error",
                "message": "City parameter is required"
            }), 400

        results = graph_manager.find_connected_hotels(
            city=city,
            tags=tags if tags else None,
            min_rating=min_rating,
            limit=limit
        )

        return jsonify({
            "status": "success",
            "results": results
        })

    except Exception as e:
        print(f"Error in connected hotels endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/destinations/insights', methods=['GET'])
def get_destination_insights():
    try:
        city = request.args.get('city')

        if not city:
            return jsonify({
                "status": "error",
                "message": "City parameter is required"
            }), 400

        results = graph_manager.get_destination_insights(city=city)

        return jsonify({
            "status": "success",
            "results": results
        })

    except Exception as e:
        print(f"Error in destination insights endpoint: {str(e)}")
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

@app.teardown_appcontext
def cleanup(resp_or_exc):
    """Cleanup connections when app context ends"""
    graph_manager.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)