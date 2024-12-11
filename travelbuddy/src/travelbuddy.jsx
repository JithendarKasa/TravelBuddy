import React, { useState } from 'react';
import { Search, MapPin, Star, List, ThumbsUp, ThumbsDown, Tag } from 'lucide-react';

const TravelBuddy = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [hotels, setHotels] = useState([]);
  const [similarHotels, setSimilarHotels] = useState([]);
  const [error, setError] = useState(null);
  const [selectedNationality, setSelectedNationality] = useState('');

  // Location tags
  const locationTags = ['Amsterdam', 'London', 'Barcelona', 'Vienna', 'Milan', 'Paris'];

  // Feature tags from Excel data
  const featureTags = [
    'Leisure trip',
    'Couple',
    'Business trip',
    'Solo traveler',
    'Family with young children',
    'Group'
  ];

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://127.0.0.1:5000/api/recommendations/location/${encodeURIComponent(searchQuery)}`);
      const result = await response.json();
      console.log('Search results:', result);

      if (result.status === 'success' && result.recommended_hotels?.length > 0) {
        setHotels(result.recommended_hotels);
      } else {
        setHotels([]);
        setError('No hotels found for this search');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to fetch hotels. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTagClick = async (tag) => {
    setLoading(true);
    setError(null);
    
    try {
      let endpoint;
      if (locationTags.includes(tag)) {
        endpoint = `location/${encodeURIComponent(tag)}`;
      } else if (featureTags.includes(tag)) {
        endpoint = `tags/${encodeURIComponent(tag)}`;
      } else {
        endpoint = `personalized?trip_type=${encodeURIComponent(tag)}`;
      }
  
      const response = await fetch(`http://127.0.0.1:5000/api/recommendations/${endpoint}`);
      const result = await response.json();
  
      if (result.status === 'error') {
        throw new Error(result.message);
      }
  
      if (result.recommended_hotels?.length > 0) {
        setHotels(result.recommended_hotels);
      } else {
        setHotels([]);
        setError(`No hotels found for ${tag}`);
      }
    } catch (err) {
      console.error('Tag search error:', err);
      setError('Failed to fetch hotels. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getSimilarHotels = async (hotelName) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/recommendations/similar/${encodeURIComponent(hotelName)}`
      );
      const result = await response.json();

      if (result.status === 'success' && result.similar_hotels?.length > 0) {
        setSimilarHotels(result.similar_hotels);
      }
    } catch (err) {
      console.error('Error fetching similar hotels:', err);
    }
  };

  const handleHotelClick = async (hotelName) => {
    await getSimilarHotels(hotelName);
    // You might want to show these in a modal or a separate section
  };

  const renderReviewContent = (review) => {
    if (typeof review === 'string' && review.trim() !== '') {
      const trimmedReview = review.length > 300 ? `${review.substring(0, 300)}...` : review;
      return <div className="review-content">{trimmedReview}</div>;
    }
    return null;
  };

  const getReviewText = (hotel, type) => {
    const review = type === 'positive' ? hotel.positive_review : hotel.negative_review;
    if (!review) return null;

    if (hotel.recent_reviews && hotel.recent_reviews.length > 0) {
      const recentReview = hotel.recent_reviews[0];
      return type === 'positive' ? recentReview.positive : recentReview.negative;
    }

    return review;
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

        <div className="tags-section">
          <h3 className="tags-title">Popular Destinations</h3>
          <div className="tags-container">
            {locationTags.map((tag) => (
              <button
                key={tag}
                className="tag-button"
                onClick={() => handleTagClick(tag)}
              >
                <MapPin size={14} className="mr-1" />
                {tag}
              </button>
            ))}
          </div>
        </div>

        <div className="tags-section">
          <h3 className="tags-title">Search by Type</h3>
          <div className="tags-container">
            {featureTags.map((tag) => (
              <button
                key={tag}
                className="tag-button"
                onClick={() => handleTagClick(tag)}
              >
                <Tag size={14} className="mr-1" />
                {tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && (
        <div className="loading">
          Loading hotels...
        </div>
      )}

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      <div className="hotel-grid">
        {hotels.map((hotel, index) => (
          <div
            key={`${hotel.name}-${index}`}
            className="hotel-card"
            onClick={() => handleHotelClick(hotel.name)}
          >
            <div className="hotel-header">
              <h2 className="hotel-name">{hotel.name}</h2>
              <div className="rating">
                <Star className="fill-current" size={20} />
                <span>{typeof hotel.rating === 'number' ? hotel.rating.toFixed(1) : 'N/A'}</span>
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

            {getReviewText(hotel, 'positive') && (
              <div className="review-section highlights">
                <div className="review-header">
                  <ThumbsUp size={18} />
                  <span>Highlights</span>
                </div>
                {renderReviewContent(getReviewText(hotel, 'positive'))}
              </div>
            )}

            {getReviewText(hotel, 'negative') && (
              <div className="review-section consider">
                <div className="review-header">
                  <ThumbsDown size={18} />
                  <span>Consider</span>
                </div>
                {renderReviewContent(getReviewText(hotel, 'negative'))}
              </div>
            )}

            {hotel.tags && (
              <div className="hotel-tags">
                <div className="review-header">
                  <Tag size={18} />
                  <span>Features</span>
                </div>
                <div className="tags-content">
                  {hotel.tags.split(',').map((tag, idx) => (
                    <span
                      key={idx}
                      className="hotel-tag"
                      onClick={() => handleTagClick(tag.trim())}
                    >
                      {tag.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {similarHotels.length > 0 && (
        <div className="similar-hotels-section">
          <h3 className="section-title">Similar Hotels</h3>
          <div className="hotel-grid">
            {similarHotels.map((hotel, index) => (
              <div
                key={`similar-${hotel.name}-${index}`}
                className="hotel-card"
                onClick={() => handleHotelClick(hotel.name)}
              >
                <h2 className="hotel-name">{hotel.name}</h2>
                <span>{hotel.location}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TravelBuddy;
