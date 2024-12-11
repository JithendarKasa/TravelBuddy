import React, { useState, useEffect } from 'react';
import { getConnectedHotels } from '../App';
import { Building2, Star, Tag } from 'lucide-react';

const ConnectedHotels = ({ city, tags, minRating = 4.0 }) => {
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchConnectedHotels = async () => {
      if (!city) return;

      try {
        setLoading(true);
        setError(null);
        const data = await getConnectedHotels(city, tags, minRating);
        setHotels(data);
      } catch (err) {
        setError('Failed to load connected hotels');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchConnectedHotels();
  }, [city, tags, minRating]);

  if (loading) return <div className="p-4 text-center">Loading connected hotels...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (!hotels.length) return <div className="p-4 text-center">No connected hotels found</div>;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <Building2 className="w-6 h-6 text-blue-500" />
        <h2 className="text-xl font-semibold">Hotels in and around {city}</h2>
      </div>

      <div className="grid gap-6">
        {hotels.map((hotel, index) => (
          <div key={index} className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-medium">{hotel.hotel_name}</h3>
              <div className="flex items-center gap-1">
                <Star className="w-5 h-5 text-yellow-400 fill-current" />
                <span>{hotel.rating.toFixed(1)}</span>
              </div>
            </div>

            <div className="text-sm text-gray-600 mb-3">
              <span className="font-medium">Location:</span> {hotel.city}
            </div>

            <div className="flex flex-wrap gap-2 mb-4">
              {hotel.hotel_tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="bg-blue-50 text-blue-700 px-2 py-1 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>

            {hotel.nearby_hotels.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium mb-2">Nearby Similar Hotels:</h4>
                <div className="grid gap-2">
                  {hotel.nearby_hotels.map((nearby, idx) => (
                    <div key={idx} className="bg-gray-50 rounded p-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span>{nearby.name}</span>
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                          <span>{nearby.rating.toFixed(1)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConnectedHotels;