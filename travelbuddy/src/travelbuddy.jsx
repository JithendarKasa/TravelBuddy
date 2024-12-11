import React, { useState } from 'react';
import { Search, MapPin, Star, List, ThumbsUp, ThumbsDown, Tag } from 'lucide-react';

const TravelBuddy = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [hotels, setHotels] = useState([]);
  const [similarHotels, setSimilarHotels] = useState([]);
  const [error, setError] = useState(null);

  // Popular destinations
  const locationTags = ['Amsterdam', 'London', 'Barcelona', 'Vienna', 'Milan', 'Paris'];

  // Travel types/features
  const featureTags = [
    'Leisure trip',
    'Couple',
    'Business trip',
    'Solo traveler',
    'Family with young children',
    'Group'
  ];

  // Handle location or feature-based search
  const handleTagClick = async (tag) => {
    setLoading(true);
    setError(null);

    try {
      const endpoint = locationTags.includes(tag)
        ? `location/${encodeURIComponent(tag)}`
        : `travel-type/${encodeURIComponent(tag)}`;
      const response = await fetch(`http://127.0.0.1:5000/api/recommendations/${endpoint}`);
      const result = await response.json();

      if (result.status === 'success' && result.recommended_hotels?.length > 0) {
        setHotels(result.recommended_hotels);
      } else {
        setHotels([]);
        setError(`No hotels found for ${tag}`);
      }
    } catch (err) {
      console.error('Error fetching tag-based recommendations:', err);
      setError('Failed to fetch recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle personalized recommendations
  const fetchPersonalizedRecommendations = async (preferences) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/recommendations/personalized', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preferences),
      });
      const result = await response.json();

      if (result.status === 'success' && result.recommended_hotels?.length > 0) {
        setHotels(result.recommended_hotels);
      } else {
        setHotels([]);
        setError('No personalized recommendations found.');
      }
    } catch (err) {
      console.error('Error fetching personalized recommendations:', err);
      setError('Failed to fetch recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch similar hotels
  const fetchSimilarHotels = async (hotelName) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/recommendations/similar/${encodeURIComponent(hotelName)}`);
      const result = await response.json();

      if (result.status === 'success' && result.similar_hotels?.length > 0) {
        setSimilarHotels(result.similar_hotels);
      }
    } catch (err) {
      console.error('Error fetching similar hotels:', err);
    }
  };

  // Render review content with trimming
  const renderReviewContent = (review) => {
    if (!review || typeof review !== 'string') return null;
    const trimmedReview = review.length > 150 ? `${review.substring(0, 150)}...` : review;
    return <div>{trimmedReview}</div>;
  };

  // Render the list of hotels
  const renderHotels = () => (
    <div className="hotel-grid">
      {hotels.map((hotel, index) => (
        <div key={`${hotel.name}-${index}`} className="hotel-card" onClick={() => fetchSimilarHotels(hotel.name)}>
          <h3>{hotel.name}</h3>
          <p><MapPin size={14} /> {hotel.location}</p>
          <p><Star size={14} /> {hotel.rating ? hotel.rating.toFixed(1) : 'N/A'}</p>
          <p><List size={14} /> {hotel.total_reviews} Reviews</p>
          <div>
            <ThumbsUp size={14} /> {renderReviewContent(hotel.positive_review)}
          </div>
          <div>
            <ThumbsDown size={14} /> {renderReviewContent(hotel.negative_review)}
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div>
      <header>
        <h1>TravelBuddy</h1>
        <p>Your personalized travel companion</p>
      </header>

      <div>
        <form onSubmit={(e) => { e.preventDefault(); handleTagClick(searchQuery); }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search destinations or tags..."
          />
          <button type="submit">
            <Search size={20} />
          </button>
        </form>

        <div>
          <h3>Popular Destinations</h3>
          {locationTags.map((tag) => (
            <button key={tag} onClick={() => handleTagClick(tag)}>
              {tag}
            </button>
          ))}
        </div>

        <div>
          <h3>Travel Types</h3>
          {featureTags.map((tag) => (
            <button key={tag} onClick={() => handleTagClick(tag)}>
              {tag}
            </button>
          ))}
        </div>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}

      {hotels.length > 0 ? renderHotels() : <p>No hotels to display.</p>}

      {similarHotels.length > 0 && (
        <div>
          <h3>Similar Hotels</h3>
          {similarHotels.map((hotel) => (
            <div key={hotel.name}>
              <h4>{hotel.name}</h4>
              <p>{hotel.location}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TravelBuddy;
