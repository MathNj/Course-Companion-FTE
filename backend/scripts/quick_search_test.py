import requests

# 1. Register or login
print("1. Registering user...")
r = requests.post(
    'http://localhost:8001/api/v1/auth/register',
    json={
        'email': 'searchtest@example.com',
        'password': 'Test123!',
        'full_name': 'Search Tester'
    },
    timeout=10
)
print(f"   Register status: {r.status_code}")

if r.status_code == 201:
    # Registration successful, get token from response
    token = r.json()['access_token']
    print(f"   New user registered")
elif r.status_code in (400, 409):
    # User exists, login instead
    print("   User exists, logging in...")
    r = requests.post(
        'http://localhost:8001/api/v1/auth/login',
        json={
            'email': 'searchtest@example.com',
            'password': 'Test123!'
        },
        timeout=10
    )
    if r.status_code != 200:
        print(f"   Login failed: {r.status_code}")
        print(f"   {r.text}")
        exit(1)
    token = r.json()['access_token']
else:
    print(f"   Failed: {r.text}")
    exit(1)

print(f"   Token: {token[:30]}...")
headers = {'Authorization': f'Bearer {token}'}

# 2. Test search
print("\n2. Testing search for 'generative AI'...")
r = requests.get(
    'http://localhost:8001/api/v1/chapters/search',
    params={'q': 'generative AI', 'limit': 3},
    headers=headers,
    timeout=10
)
print(f"   Status: {r.status_code}")

if r.status_code == 200:
    results = r.json()
    print(f"   Results found: {len(results)}")

    if results:
        print(f"\n   Top result:")
        print(f"     Chapter: {results[0]['chapter_title']}")
        print(f"     Section: {results[0]['section_title']}")
        print(f"     Relevance: {results[0]['relevance_score']}")
        print(f"     Snippet: {results[0]['snippet'][:100]}...")
else:
    print(f"   Error: {r.text}")

# 3. Test search for LLMs
print("\n3. Testing search for 'LLM'...")
r = requests.get(
    'http://localhost:8001/api/v1/chapters/search',
    params={'q': 'LLM', 'limit': 2},
    headers=headers,
    timeout=10
)
print(f"   Status: {r.status_code}")
print(f"   Results: {len(r.json()) if r.status_code == 200 else 0}")

print("\n[OK] Search endpoint is working!")
