"""
tests/test_integration.py
Integration tests for the complete system
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_complete_workflow():
    """Test complete user workflow"""
    
    # 1. Get trending products
    response = client.get("/api/v1/trends/products?min_score=0.6&limit=5")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    
    # 2. Get product details
    product_id = products[0]["id"]
    response = client.get(f"/api/v1/trends/products/{product_id}")
    assert response.status_code == 200
    
    # 3. Create alert
    alert_data = {
        "user_id": "integration_test_user",
        "keywords": ["tech"],
        "categories": ["Electronics"],
        "min_trend_score": 0.7,
        "platforms": ["amazon"]
    }
    response = client.post("/api/v1/alerts/", json=alert_data)
    assert response.status_code == 200
    alert_id = response.json()["id"]
    
    # 4. Check alert
    response = client.get(f"/api/v1/alerts/{alert_id}/check")
    assert response.status_code == 200


@pytest.mark.integration
def test_merchant_workflow():
    """Test merchant-specific workflow"""
    
    # Get merchant insights
    response = client.get("/api/v1/trends/products?min_score=0.7&limit=10")
    assert response.status_code == 200
    
    products = response.json()
    if products:
        product_id = products[0]["id"]
        
        # Get merchant insights
        response = client.get(f"/api/v1/products/merchant-insights/{product_id}")
        assert response.status_code == 200
        insights = response.json()
        assert "competition_level" in insights


@pytest.mark.integration
def test_consumer_workflow():
    """Test consumer-specific workflow"""
    
    # Get events
    response = client.get("/api/v1/products/events?days_ahead=30")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    
    # Compare prices
    response = client.get("/api/v1/products/compare/test%20product")
    assert response.status_code == 200
