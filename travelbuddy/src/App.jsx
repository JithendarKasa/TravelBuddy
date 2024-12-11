import React from 'react';
import TravelBuddy from './travelbuddy';

const App = () => {
  return (
    <div>
      <TravelBuddy />
    </div>
  );
};

const API_BASE_URL = 'http://127.0.0.1:5000';

export const searchHotels = async (params) => {
    const queryParams = new URLSearchParams();
    if (params.features) {
        params.features.forEach(feature => queryParams.append('features', feature));
    }
    if (params.searchText) {
        queryParams.append('search_text', params.searchText);
    }
    if (params.limit) {
        queryParams.append('limit', params.limit);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/hotels/search?${queryParams}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.results;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error searching hotels:', error);
        throw error;
    }
};

export const getFeatures = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/hotels/features`);
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.features;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error getting features:', error);
        throw error;
    }
};

export const getRelatedDestinations = async (city, tagType = null, limit = 5) => {
    try {
        const queryParams = new URLSearchParams({
            city: city,
            limit: limit
        });
        
        if (tagType) {
            queryParams.append('tag_type', tagType);
        }

        const response = await fetch(`${API_BASE_URL}/destinations/related?${queryParams}`);
        const data = await response.json();

        if (data.status === 'success') {
            return data.results;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error getting related destinations:', error);
        throw error;
    }
};

export const getConnectedHotels = async (city, tags = [], minRating = 4.0, limit = 10) => {
    try {
        const queryParams = new URLSearchParams({
            city: city,
            min_rating: minRating,
            limit: limit
        });

        tags.forEach(tag => queryParams.append('tags', tag));

        const response = await fetch(`${API_BASE_URL}/destinations/hotels?${queryParams}`);
        const data = await response.json();

        if (data.status === 'success') {
            return data.results;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error getting connected hotels:', error);
        throw error;
    }
};

export const getDestinationInsights = async (city) => {
    try {
        const queryParams = new URLSearchParams({
            city: city
        });

        const response = await fetch(`${API_BASE_URL}/destinations/insights?${queryParams}`);
        const data = await response.json();

        if (data.status === 'success') {
            return data.results;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error getting destination insights:', error);
        throw error;
    }
};

export default App;