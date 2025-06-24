// auth.js

export function saveToken(token) {
  localStorage.setItem("access_token", token);
}

export function getToken() {
  return localStorage.getItem("access_token");
}

export function isAuthenticated() {
  return !!getToken(); // retorna true se houver token
}

export function logout() {
  localStorage.removeItem("access_token");
  window.location.href = "/auth/";
}

export function requireAuth() {
  if (!isAuthenticated()) {
    localStorage.removeItem("access_token");
    window.location.href = "/auth/";
  }
}
