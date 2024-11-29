const API_BASE_URL = 'http://127.0.0.1:5000/api';

export const searchHotels = async (query) => {
  try {
    const response = await fetch(`${API_BASE_URL}/recommendations/location/${encodeURIComponent(query)}`);
    const data = await response.json();
    console.log('API Response:', data); // For debugging
    return data;
  } catch (error) {
    console.error('Error fetching hotels:', error);
    throw error;
  }
};