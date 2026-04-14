import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
});

// Add a request interceptor to include the JWT token or API Key
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  const apiKey = localStorage.getItem("apiKey");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  } else if (apiKey) {
    config.headers["X-API-Key"] = apiKey;
  }

  return config;
});

export default api;
