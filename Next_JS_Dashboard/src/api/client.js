import axios from 'axios';

const API_BASE_URL = 'https://ai-agents-fealty.onrender.com'; // Production URL

const client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default client;
