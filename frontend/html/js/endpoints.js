// endpoints.js

const BASE_URL = "http://localhost:8000"; // or change to your production URL

export const endpoints = {
  auth: {
    register: `${BASE_URL}/register`,
    login: `${BASE_URL}/login`,
    logout: `${BASE_URL}/logout`,
  },
  subscriptions: {
    add: `${BASE_URL}/subscriptions`,
    list: `${BASE_URL}/subscriptions`,
    update: (serviceName) => `${BASE_URL}/subscriptions/${serviceName}`, // Added update endpoint
    delete: (serviceName) => `${BASE_URL}/subscriptions/${serviceName}`,
  },
  analytics: {
    search: `${BASE_URL}/analytics/search`, // Updated path
    summary: `${BASE_URL}/analytics/summary`, // Updated path
    categories: `${BASE_URL}/analytics/categories`, // Updated path
  },
  system: {
    rootInfo: `${BASE_URL}/`, // Corresponds to GET /
    health: `${BASE_URL}/health`, // Corresponds to GET /health
  },
};