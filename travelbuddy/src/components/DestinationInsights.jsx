import React, { useState, useEffect } from 'react';
import { getDestinationInsights } from '../App';
import { BarChart, Hotel, Info, MessagesSquare } from 'lucide-react';

const DestinationInsights = ({ city }) => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInsights = async () => {
      if (!city) return;
      
      try {
        setLoading(true);
        setError(null);
        const data = await getDestinationInsights(city);
        setInsights(data);
      } catch (err) {
        setError('Failed to load destination insights');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [city]);

  if (loading) return <div className="p-4 text-center">Loading insights...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (!insights) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Info className="w-6 h-6 text-blue-500" />
        <h2 className="text-xl font-semibold">Insights for {city}</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Hotel className="w-5 h-5 text-blue-600" />
            <h3 className="font-medium">Hotels</h3>
          </div>
          <p className="text-2xl font-bold">{insights.hotel_count}</p>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <BarChart className="w-5 h-5 text-blue-600" />
            <h3 className="font-medium">Average Rating</h3>
          </div>
          <p className="text-2xl font-bold">{insights.avg_rating.toFixed(1)}</p>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <MessagesSquare className="w-5 h-5 text-blue-600" />
            <h3 className="font-medium">Total Reviews</h3>
          </div>
          <p className="text-2xl font-bold">{insights.total_reviews.toLocaleString()}</p>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="font-medium mb-3">Popular Tags</h3>
        <div className="flex flex-wrap gap-2">
          {insights.tags.map((tag, index) => (
            <span
              key={index}
              className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DestinationInsights;