// endpoints.js

const BASE_URL = "http://localhost:8000"; // ou altera para tua URL de produção

export const endpoints = {
  auth: {
    register: `${BASE_URL}/register`,
    login: `${BASE_URL}/login`,
    logout: `${BASE_URL}/logout`,
  },
  subscriptions: {
    add: `${BASE_URL}/subscriptions`,
    list: `${BASE_URL}/subscriptions`,
    delete: (serviceName) => `${BASE_URL}/subscriptions/${serviceName}`, // usa: delete('Netflix')
  },
  analytics: {
    search: (term) => `${BASE_URL}/search?term=${encodeURIComponent(term)}`,
    summary: `${BASE_URL}/summary`,
    categories: `${BASE_URL}/categories`,
  },
  system: {
    info: `${BASE_URL}/system/`,
  },
};
