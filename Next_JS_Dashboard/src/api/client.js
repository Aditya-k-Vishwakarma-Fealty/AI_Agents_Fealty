import axios from 'axios';

/**
 * Default to local API in development. Set NEXT_PUBLIC_API_URL for production
 * (e.g. https://your-api.onrender.com) so the dashboard does not call a remote
 * host on every save during local work.
 */
const API_BASE_URL = (
  typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL
    ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '')
    : 'http://127.0.0.1:8000'
);

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default client;
export { API_BASE_URL };
