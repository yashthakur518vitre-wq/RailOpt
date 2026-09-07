import axios from 'axios';

// When opened from another device, localhost would point to that device itself.
// Use the same host as the Vite page and port 8000 for the local FastAPI server.
const configuredBase = import.meta.env.VITE_API_BASE_URL?.trim();
const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
const baseURL = configuredBase || `http://${host}:8000`;

const client = axios.create({
  baseURL: `${baseURL.replace(/\/$/, '')}/api`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

export default client;
