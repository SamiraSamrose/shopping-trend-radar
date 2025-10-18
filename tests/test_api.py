"""
tests/test_api.py
API endpoint tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_info():
    """Test API info endpoint"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()


def test_get_trending_products():
    """Test trending products endpoint"""
    response = client.get("/api/v1/trends/products?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_trending_categories():
    """Test trending categories endpoint"""
    response = client.get("/api/v1/trends/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_alert():
    """Test alert creation"""
    alert_data = {
        "user_id": "test_user",
        "keywords": ["test"],
        "categories": ["Electronics"],
        "min_trend_score": 0.7,
        "platforms": ["amazon"]
    }
    response = client.post("/api/v1/alerts/", json=alert_data)
    assert response.status_code == 200
    assert "id" in response.json()


def test_get_event_recommendations():
    """Test event recommendations"""
    response = client.get("/api/v1/products/events?days_ahead=30")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_invalid_product_id():
    """Test invalid product ID handling"""
    response = client.get("/api/v1/trends/products/invalid_id")
    assert response.status_code == 404
