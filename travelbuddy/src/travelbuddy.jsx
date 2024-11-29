import React, { useState, useEffect } from 'react';
import { Search, MapPin, Star, List, ThumbsUp, ThumbsDown } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const TravelBuddy = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const tags = ['family-friendly', 'business', 'luxury', 'beach', 'city center'];

  // Function to fetch hotels from backend
  const searchHotels = async (query, tags) => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams();
      
      if (query) {
        queryParams.append('search_text', query);
      }
      
      tags.forEach(tag => {
        queryParams.append('features', tag);
      });

      const response = await fetch(`${API_BASE_URL}/hotels/search?${queryParams}`);
      const data = await response.json();

      if (data.status === 'success') {
        // Transform the data to match your UI structure
        const transformedHotels = data.results.map((hotel, index) => ({
          id: index + 1,
          name: hotel.name,
          location: hotel.location,
          rating: hotel.averageReviewScore,
          reviews: hotel.reviewCount,
          positiveReviews: hotel.highlights || [],
          negativeReviews: hotel.considerations || [],
          tags: hotel.tags || []
        }));

        setHotels(transformedHotels);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to fetch hotels. Please try again.');
      console.error('Error fetching hotels:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle tag selection
  const toggleTag = (tag) => {
    setSelectedTags(prev => {
      if (prev.includes(tag)) {
        return prev.filter(t => t !== tag);
      }
      return [...prev, tag];
    });
  };

  // Search when tags or query changes
  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      searchHotels(searchQuery, selectedTags);
    }, 500); // Debounce search for 500ms

    return () => clearTimeout(delayDebounce);
  }, [searchQuery, selectedTags]);

  return (
    <div className="container">
      <header className="header">
        <h1>TravelBuddy</h1>
        <p>Intelligent Hotel Search & Destination Insights</p>
      </header>

      <div className="search-container">
        <div className="search-wrapper">
          <input
            type="text"
            placeholder="Search hotels, destinations, or amenities..."
            className="search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Search className="search-icon" size={20} />
        </div>

        <div className="tags-container">
          {tags.map((tag) => (
            <button
              key={tag}
              className={`tag-button ${selectedTags.includes(tag) ? 'selected' : ''}`}
              onClick={() => toggleTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="loading">Loading hotels...</div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="hotel-grid">
        {hotels.map((hotel) => (
          <div key={hotel.id} className="hotel-card">
            <div className="hotel-header">
              <h2 className="hotel-name">{hotel.name}</h2>
              <div className="rating">
                <Star className="fill-current" size={20} />
                <span>{hotel.rating}</span>
              </div>
            </div>

            <div className="location">
              <MapPin size={18} />
              <span>{hotel.location}</span>
            </div>

            <div className="reviews-count">
              <List size={18} />
              <span>{hotel.reviews} Reviews</span>
            </div>

            {hotel.positiveReviews.length > 0 && (
              <div className="review-section highlights">
                <div className="review-header">
                  <ThumbsUp size={18} />
                  <span>Highlights</span>
                </div>
                <ul className="review-list">
                  {hotel.positiveReviews.map((review, idx) => (
                    <li key={idx}>{review}</li>
                  ))}
                </ul>
              </div>
            )}

            {hotel.negativeReviews.length > 0 && (
              <div className="review-section consider">
                <div className="review-header">
                  <ThumbsDown size={18} />
                  <span>Consider</span>
                </div>
                <ul className="review-list">
                  {hotel.negativeReviews.map((review, idx) => (
                    <li key={idx}>{review}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="hotel-tags">
              {hotel.tags.map((tag, idx) => (
                <span key={idx} className="hotel-tag">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TravelBuddy;