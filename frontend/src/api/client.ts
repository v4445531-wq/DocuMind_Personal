import axios from "axios";

import { clearToken, getToken } from "../auth/token";

// Use relative URLs so the frontend works on any host (localhost, Fly.io, etc.)
// The reverse proxy (nginx on Fly.io, Vite dev proxy locally) routes /api/ and /auth/ to the gateway.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach the JWT to every request if we have one.
apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If the gateway rejects the token, drop it so the app falls back to login.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      clearToken();
    }
    return Promise.reject(error);
  },
);
