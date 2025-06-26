// endpoints.js

const BASE_URL = "http://localhost:8000";

export const endpoints = {
  auth: {
    register: `${BASE_URL}/register`,
    login: `${BASE_URL}/login`,
    logout: `${BASE_URL}/logout`,
  },
  subscriptions: {
    add: `${BASE_URL}/subscriptions`,
    list: `${BASE_URL}/subscriptions`,
    update: (serviceName) => `${BASE_URL}/subscriptions/${serviceName}`, 
    delete: (serviceName) => `${BASE_URL}/subscriptions/${serviceName}`,
  },
  analytics: {
    search: `${BASE_URL}/analytics/search`,
    summary: `${BASE_URL}/analytics/summary`,
    categories: `${BASE_URL}/analytics/categories`,
  },
  system: {
    rootInfo: `${BASE_URL}/`,
    health: `${BASE_URL}/health`, 
  },
};