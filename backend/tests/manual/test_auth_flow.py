import requests

BASE_URL = "http://localhost:8000"

EMAIL = "test@example.com"
USERNAME = "testuser"
PASSWORD = "testpassword"

# Step 1 – Register
def register():
    print("[*] Registering user...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "username": USERNAME,
        "email": EMAIL,
        "password": PASSWORD
    })
    print(f"Status {resp.status_code}:", resp.json())

# Step 2 – Login
def login():
    print("[*] Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login", data={
        "email": EMAIL,
        "password": PASSWORD
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})

    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print(f"[+] Received token: {token[:20]}...")
        return token
    else:
        print("[-] Login failed:", resp.json())
        return None

# Step 3 – Access Protected Route
def test_protected(token):
    print("[*] Testing protected route...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/auth/protected", headers=headers)
    print(f"Status {resp.status_code}:", resp.json())

if __name__ == "__main__":
    register()
    token = login()
    if token:
        test_protected(token)
