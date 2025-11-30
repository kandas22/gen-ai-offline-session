import requests
import uuid

BASE_URL = 'http://localhost:5001/api'

def run_verification():
    # 1. Register
    email = f"test_{uuid.uuid4()}@example.com"
    print(f"Registering user: {email}")
    res = requests.post(f"{BASE_URL}/auth/register", json={'email': email})
    if res.status_code != 201:
        print(f"Registration failed: {res.text}")
        return
    print("Registration successful")

    # 2. Login
    print("Logging in...")
    res = requests.post(f"{BASE_URL}/auth/login", json={'email': email})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
    token = res.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("Login successful")

    # 3. Create Subscription
    print("Creating subscription...")
    sub_data = {
        'name': 'Netflix',
        'cost': 15.99,
        'category': 'streaming',
        'start_date': '2023-01-01'
    }
    res = requests.post(f"{BASE_URL}/subscriptions/", json=sub_data, headers=headers)
    if res.status_code != 201:
        print(f"Create subscription failed: {res.text}")
        return
    sub_id = res.json()['id']
    print(f"Subscription created: {sub_id}")

    # 4. Get Analytics (should be low effectiveness)
    print("Checking analytics (expecting low score)...")
    res = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
    print(f"Analytics: {res.json()}")

if __name__ == '__main__':
    run_verification()
