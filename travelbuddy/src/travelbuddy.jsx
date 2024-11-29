import React, { useState } from 'react';
import { Search, MapPin, Star, List, ThumbsUp, ThumbsDown } from 'lucide-react';

const TravelBuddy = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [hotels, setHotels] = useState([]);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://127.0.0.1:5000/api/recommendations/location/${encodeURIComponent(searchQuery)}`);
      const result = await response.json();
      console.log('Search results:', result);
      
      if (result.recommended_hotels && result.recommended_hotels.length > 0) {
        setHotels(result.recommended_hotels);
      } else {
        setHotels([]);
        setError('No hotels found');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to fetch hotels. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTagClick = (tag) => {
    setSearchQuery(tag);
    handleSearch({ preventDefault: () => {} });
  };

  return (
    <div className="container">
      <header className="header">
        <h1>TravelBuddy</h1>
        <p>Intelligent Hotel Search & Destination Insights</p>
      </header>

      <div className="search-container">
        <form onSubmit={handleSearch}>
          <div className="search-wrapper">
            <input
              type="text"
              placeholder="Search hotels, destinations, or amenities..."
              className="search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" className="search-button">
              <Search className="search-icon" size={20} />
            </button>
          </div>
        </form>

        <div className="tags-container">
          {['Amsterdam', 'London', 'Barcelona', 'Vienna', 'Milan'].map((tag) => (
            <button 
              key={tag} 
              className="tag-button"
              onClick={() => handleTagClick(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error">{error}</div>}

      <div className="hotel-grid">
        {hotels.map((hotel, index) => (
          <div key={index} className="hotel-card">
            <div className="hotel-header">
              <h2 className="hotel-name">{hotel.name}</h2>
              <div className="rating">
                <Star className="fill-current" size={20} />
                <span>{parseFloat(hotel.rating).toFixed(1)}</span>
              </div>
            </div>

            <div className="location">
              <MapPin size={18} />
              <span>{hotel.location}</span>
            </div>

            <div className="reviews-count">
              <List size={18} />
              <span>{hotel.total_reviews || 0} Reviews</span>
            </div>

            {hotel.recent_review && (
              <>
                <div className="review-section highlights">
                  <div className="review-header">
                    <ThumbsUp size={18} />
                    <span>Highlights</span>
                  </div>
                  <ul className="review-list">
                    <li>{hotel.recent_review.positive || 'No positive review available'}</li>
                  </ul>
                </div>

                <div className="review-section consider">
                  <div className="review-header">
                    <ThumbsDown size={18} />
                    <span>Consider</span>
                  </div>
                  <ul className="review-list">
                    <li>{hotel.recent_review.negative || 'No negative review available'}</li>
                  </ul>
                </div>
              </>
            )}

            {hotel.tags && (
              <div className="hotel-tags">
                {hotel.tags.split(',').map((tag, idx) => (
                  <span key={idx} className="hotel-tag">
                    {tag.trim()}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TravelBuddy;