import React, { useState, useEffect } from 'react';
import { Search, MapPin, Star, List, ThumbsUp, ThumbsDown } from 'lucide-react';
import DestinationInsights from './components/DestinationInsights';
import RelatedDestinations from './components/RelatedDestinations';
import ConnectedHotels from './components/ConnectedHotels';

const API_BASE_URL = 'http://127.0.0.1:5000';

const TravelBuddy = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCity, setSelectedCity] = useState('');
  const [showDestinationInfo, setShowDestinationInfo] = useState(false);

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

        // If we have hotels and no city is selected, set the city from the first hotel
        if (transformedHotels.length > 0 && !selectedCity) {
          const cityFromHotel = transformedHotels[0].location.split(',')[0].trim();
          setSelectedCity(cityFromHotel);
        }
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

  // Handle hotel card click
  const handleHotelClick = (hotel) => {
    // const city = hotel.location.split(',')[0].trim();
    // setSelectedCity(city);
    // setShowDestinationInfo(true);
    console.log('Hotel clicked:', hotel);
    const parts = hotel.location.split(' ');
    const majorCities = ['Paris', 'London', 'Rome', 'Barcelona', 'Vienna', 'Amsterdam'];
    const city = parts.find(part => majorCities.includes(part)) || parts[0];
    setSelectedCity(city);
    setShowDestinationInfo(true);
  };

  // Search when tags or query changes
  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      searchHotels(searchQuery, selectedTags);
    }, 500); // Debounce search for 500ms

    return () => clearTimeout(delayDebounce);
  }, [searchQuery, selectedTags]);

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">TravelBuddy</h1>
        <p className="text-gray-600">Intelligent Hotel Search & Destination Insights</p>
      </header>
  
      <div className="mb-8">
        {/* Search Bar Wrapper */}
        <div className="search-wrapper relative max-w-2xl mx-auto mb-4">
          <input
            type="text"
            placeholder="Search hotels, destinations, or amenities..."
            className="search-input w-full px-4 py-2 border rounded-lg pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Search className="search-icon absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
        </div>
  
        {/* Tags Section */}
        <div className="flex flex-wrap justify-center gap-2">
          {tags.map((tag) => (
            <button
              key={tag}
              className={`px-4 py-2 rounded-full text-sm transition-colors ${
                selectedTags.includes(tag)
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }`}
              onClick={() => toggleTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>
  
      {/* Loading and Error Messages */}
      {loading && <div className="text-center py-8">Loading hotels...</div>}
  
      {error && (
        <div className="text-red-500 text-center py-4">{error}</div>
      )}
  
      {/* Hotel Grid Layout */}
      <div className="hotel-grid">
        {hotels.map((hotel) => (
          <div
            key={hotel.id}
            className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow"
            onClick={() => handleHotelClick(hotel)}
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">{hotel.name}</h2>
              <div className="flex items-center gap-1">
                <Star className="text-yellow-400 fill-current" size={20} />
                <span className="font-medium">{hotel.rating}</span>
              </div>
            </div>
  
            <div className="flex items-center gap-2 text-gray-600 mb-3">
              <MapPin size={18} />
              <span>{hotel.location}</span>
            </div>
  
            <div className="flex items-center gap-2 text-gray-600 mb-4">
              <List size={18} />
              <span>{hotel.reviews} Reviews</span>
            </div>
  
            {/* Highlights Section */}
            {hotel.positiveReviews.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <ThumbsUp size={18} className="text-green-500" />
                  <span className="font-medium">Highlights</span>
                </div>
                <ul className="space-y-2">
                  {hotel.positiveReviews.map((review, idx) => (
                    <li key={idx} className="text-gray-600 text-sm">
                      {review}
                    </li>
                  ))}
                </ul>
              </div>
            )}
  
            {/* Consider Section */}
            {hotel.negativeReviews.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <ThumbsDown size={18} className="text-red-500" />
                  <span className="font-medium">Consider</span>
                </div>
                <ul className="space-y-2">
                  {hotel.negativeReviews.map((review, idx) => (
                    <li key={idx} className="text-gray-600 text-sm">
                      {review}
                    </li>
                  ))}
                </ul>
              </div>
            )}
  
            {/* Hotel Tags */}
            <div className="flex flex-wrap gap-2">
              {hotel.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
  
      {/* Destination Info Section */}
      {selectedCity && showDestinationInfo && (
        <div className="space-y-6">
          <DestinationInsights city={selectedCity} />
          <RelatedDestinations
            city={selectedCity}
            tagType={selectedTags.length > 0 ? selectedTags[0] : null}
          />
          <ConnectedHotels
            city={selectedCity}
            tags={selectedTags}
            minRating={4.0}
          />
        </div>
      )}
    </div>
  );    
};

export default TravelBuddy;
