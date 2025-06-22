# backend/tests/manual/test_subscription_flow.py

import requests

BASE_URL = "http://localhost:8000"
REGISTER_DATA = {
    "username": "subtestuser",
    "email": "subuser@example.com",
    "password": "testpass123"
}

LOGIN_DATA = {
    "email": REGISTER_DATA["email"],
    "password": REGISTER_DATA["password"]
}

subscription_payload = {
    "service_name": "Netflix",
    "category": "Streaming",
    "monthly_cost": 9.99,
    "renewal_date": "2025-07-01"
}

def main():
    print("[*] Registering user...")
    r = requests.post(f"{BASE_URL}/auth/register", json=REGISTER_DATA)
    print(f"Status {r.status_code}:", r.json())

    print("[*] Logging in...")
    r = requests.post(f"{BASE_URL}/auth/login", data=LOGIN_DATA)
    token = r.json().get("access_token")
    print("[+] Received token:", token[:30], "...")

    headers = {"Authorization": f"Bearer {token}"}

    print("[*] Creating subscription...")
    r = requests.post(f"{BASE_URL}/subscriptions/", json=subscription_payload, headers=headers)
    print(f"Status {r.status_code}:", r.json())
    sub_id = r.json().get("id")

    print("[*] Fetching all subscriptions...")
    r = requests.get(f"{BASE_URL}/subscriptions/", headers=headers)
    print(f"Status {r.status_code}:", r.json())

    print("[*] Deleting subscription...")
    r = requests.delete(f"{BASE_URL}/subscriptions/{sub_id}", headers=headers)
    print(f"Status {r.status_code}:", r.json())

if __name__ == "__main__":
    main()
