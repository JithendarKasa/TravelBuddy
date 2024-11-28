import React, { useState } from 'react';
import { Search, MapPin, Star, List, ThumbsUp, ThumbsDown } from 'lucide-react';

const TravelBuddy = () => {
  const [searchQuery, setSearchQuery] = useState('');
  
  const hotels = [
    {
      id: 1,
      name: "Grand Hotel Europa",
      location: "Paris, France",
      rating: 4.5,
      reviews: 245,
      positiveReviews: ["Great breakfast!", "Excellent location"],
      negativeReviews: ["Room was small"],
      tags: ["family-friendly", "central location"]
    },
    {
      id: 2,
      name: "Royal Gardens Hotel",
      location: "London, UK",
      rating: 4.8,
      reviews: 189,
      positiveReviews: ["Amazing staff", "Beautiful garden view"],
      negativeReviews: ["Expensive parking"],
      tags: ["luxury", "business-friendly"]
    }
  ];

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
          {['family-friendly', 'business', 'luxury', 'beach', 'city center'].map((tag) => (
            <button key={tag} className="tag-button">
              {tag}
            </button>
          ))}
        </div>
      </div>

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