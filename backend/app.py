from flask import Flask, jsonify, request
from flask_cors import CORS
from travelsearch import TravelBuddyQueries
from destination_graph import DestinationGraphManager

app = Flask(__name__)
CORS(app)

# Initialize Neo4j connection
# graph_manager = DestinationGraphManager(
#     uri="bolt://localhost:7687",
#     user="neo4j",
#     password="moderndbproject",
#     database="travelbuddy"
# )
graph_manager = DestinationGraphManager(
    uri="bolt://127.0.0.1:7687",
    user="neo4j",
    password="moderndbproject",
    database="travelbuddy"
)

def setup_database():
    try:
       
        # Initialize Neo4j schema
        graph_manager.ensure_connection()
        graph_manager.initialize_database()
        
        # Get hotel data from MongoDB
        hotel_search = TravelBuddyQueries()
        hotels = hotel_search.get_all_hotels()
        print(f"Found {len(hotels)} hotels in MongoDB")
        
        # Print sample hotel for verification
        if hotels:
            print("Sample hotel data:", hotels[0])
            
        # Create graph relationships
        graph_manager.create_hotel_destination_graph(hotels)
        
        # Verify data in Neo4j
        with graph_manager.driver.session() as session:
            # Count nodes
            hotel_count = session.run("MATCH (h:Hotel) RETURN count(h) as count").single()['count']
            city_count = session.run("MATCH (c:City) RETURN count(c) as count").single()['count']
            print(f"Neo4j contains {hotel_count} hotels and {city_count} cities")
            
            # Check relationships
            rel_count = session.run("""
                MATCH ()-[r:LOCATED_IN]->() 
                RETURN count(r) as count
            """).single()['count']
            print(f"Found {rel_count} LOCATED_IN relationships")
    except Exception as e:
        print(f"Database setup error: {str(e)}")

# Call setup directly during app initialization
with app.app_context():
    setup_database()

@app.route('/hotels/search', methods=['GET'])
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

@app.route('/destinations/related', methods=['GET'])
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

# @app.route('/destinations/hotels', methods=['GET'])
# def get_connected_hotels():
#     try:
#         city = request.args.get('city')
#         tags = request.args.getlist('tags')
#         min_rating = float(request.args.get('min_rating', 4.0))
#         limit = int(request.args.get('limit', 10))

#         if not city:
#             return jsonify({
#                 "status": "error",
#                 "message": "City parameter is required"
#             }), 400

#         results = graph_manager.find_connected_hotels(
#             city=city,
#             tags=tags if tags else None,
#             min_rating=min_rating,
#             limit=limit
#         )

#         return jsonify({
#             "status": "success",
#             "results": results
#         })

#     except Exception as e:
#         print(f"Error in connected hotels endpoint: {str(e)}")
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500


@app.route('/destinations/hotels', methods=['GET'])
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

        # Ensure connection before query
        graph_manager.ensure_connection()

        results = graph_manager.find_connected_hotels(
            city=city,
            tags=tags if tags else None,
            min_rating=min_rating,
            limit=limit
        )

        return jsonify({
            "status": "success",
            "results": results if results else []
        })

    except Exception as e:
        print(f"Error in connected hotels endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/destinations/insights', methods=['GET'])
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

@app.route('/hotels/features', methods=['GET'])
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