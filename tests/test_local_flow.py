from fastapi.testclient import TestClient
import json
import sys
import os

# Ensure project root is on sys.path so 'main' imports correctly when run from tests folder
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from main import app

client = TestClient(app)

print('GET /')
resp = client.get('/')
print(resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.text)

print('\nGET /token (before)')
resp = client.get('/token')
print(resp.status_code)
print(resp.json())

print('\nSimulate /instagram/callback?access_token=TEST_TOKEN_123')
resp = client.get('/instagram/callback', params={'access_token':'TEST_TOKEN_123'})
print(resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.text)

print('\nGET /token (after)')
resp = client.get('/token')
print(resp.status_code)
print(resp.json())

print('\nGET /instagram/profile')
resp = client.get('/instagram/profile')
print(resp.status_code)
try:
    print(json.dumps(resp.json(), indent=2))
except Exception:
    print(resp.text)

print('\nDELETE /token')
resp = client.delete('/token')
print(resp.status_code)
print(resp.json())

print('\nGET /token (final)')
resp = client.get('/token')
print(resp.status_code)
print(resp.json())
