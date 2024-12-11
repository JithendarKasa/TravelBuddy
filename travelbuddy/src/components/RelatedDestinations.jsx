import React, { useState, useEffect } from 'react';
import { getRelatedDestinations } from '../App';
import { Map, Tag } from 'lucide-react';

const RelatedDestinations = ({ city, tagType }) => {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRelatedDestinations = async () => {
      if (!city) return;

      try {
        setLoading(true);
        setError(null);
        const data = await getRelatedDestinations(city, tagType);
        setDestinations(data);
      } catch (err) {
        setError('Failed to load related destinations');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRelatedDestinations();
  }, [city, tagType]);

  if (loading) return <div className="p-4 text-center">Loading related destinations...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (!destinations.length) return <div className="p-4 text-center">No related destinations found</div>;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <Map className="w-6 h-6 text-blue-500" />
        <h2 className="text-xl font-semibold">Destinations Similar to {city}</h2>
      </div>

      <div className="grid gap-4">
        {destinations.map((dest, index) => (
          <div
            key={index}
            className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-medium">{dest.city}</h3>
              <div className="text-sm text-gray-600">
                Rating: {dest.avg_rating.toFixed(1)}
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Tag className="w-4 h-4" />
              <span>{dest.shared_tags} shared characteristics</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RelatedDestinations;