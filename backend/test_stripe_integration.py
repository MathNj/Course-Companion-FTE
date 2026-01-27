"""
Test Stripe Integration
Quick test to verify Stripe checkout flow works
"""

import requests
import json

# Production backend URL
BASE_URL = "https://course-companion-fte.fly.dev/api/v1"

print("=" * 60)
print("Testing Stripe Integration")
print("=" * 60)
print()

# Step 1: Register or login test user
print("Step 1: Getting test user credentials...")
register_response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": "stripe_test@example.com",
        "password": "TestPass123",
        "full_name": "Stripe Test User"
    }
)

# If user exists, try logging in instead
if register_response.status_code == 400:
    print("  User already exists, logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "stripe_test@example.com",
            "password": "TestPass123"
        }
    )
    if login_response.status_code in [200, 201]:
        data = login_response.json()
    else:
        print(f"[ERROR] Failed to login: {login_response.status_code}")
        print(login_response.text)
        exit(1)
elif register_response.status_code in [200, 201]:
    data = register_response.json()
else:
    print(f"[ERROR] Failed to create/login user: {register_response.status_code}")
    print(register_response.text)
    exit(1)

access_token = data["access_token"]
print(f"[OK] Test user ready")
print(f"  Email: stripe_test@example.com")
print(f"  Token: {access_token[:50]}...")
print()

# Step 2: Create checkout session
print("Step 2: Creating checkout session...")
checkout_response = requests.post(
    f"{BASE_URL}/payments/create-checkout-session",
    headers={"Authorization": f"Bearer {access_token}"},
    json={}
)

if checkout_response.status_code == 200:
    data = checkout_response.json()
    checkout_url = data.get("checkout_url")
    session_id = data.get("session_id")
    print(f"[OK] Checkout session created!")
    print(f"  Session ID: {session_id}")
    print(f"  Checkout URL: {checkout_url}")
    print()
    print(f"--> Visit this URL to complete test payment:")
    print(f"    {checkout_url}")
    print()
    print(f"--> Use test card: 4242 4242 4242 4242")
    print(f"    Expiry: Any future date (e.g., 12/34)")
    print(f"    CVC: Any 3 digits (e.g., 123)")
    print()
else:
    print(f"[ERROR] Failed to create checkout: {checkout_response.status_code}")
    print(checkout_response.text)
    exit(1)

# Step 3: Check subscription status
print("Step 3: Checking subscription status (before payment)...")
status_response = requests.get(
    f"{BASE_URL}/payments/subscription-status",
    headers={"Authorization": f"Bearer {access_token}"}
)

if status_response.status_code == 200:
    data = status_response.json()
    print(f"[OK] Subscription status retrieved")
    print(f"  Is Premium: {data['is_premium']}")
    print(f"  Status: {data.get('subscription_status', 'None')}")
    print()
else:
    print(f"[ERROR] Failed to get status: {status_response.status_code}")

print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print()
print("Next steps:")
print("1. Visit the checkout URL above")
print("2. Complete payment with test card")
print("3. Run this script again to verify premium access")
print()
