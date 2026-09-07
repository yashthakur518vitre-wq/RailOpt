import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200

def test_get_assets():
    r = client.get('/api/assets')
    assert r.status_code == 200

def test_get_maintenance():
    r = client.get('/api/maintenance')
    assert r.status_code == 200

def test_ai_model_status():
    r = client.get('/api/ai/model-status')
    assert r.status_code == 200

def test_get_corridors():
    r = client.get('/api/corridors')
    assert r.status_code == 200

def test_get_trains():
    r = client.get('/api/trains')
    assert r.status_code == 200

def test_get_dashboard_summary():
    r = client.get('/api/dashboard/summary')
    assert r.status_code == 200
