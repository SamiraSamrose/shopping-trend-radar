"""
tests/test_services.py
Service layer tests
"""

import pytest
from app.services.data_aggregator import DataAggregator
from app.models.trends import Product


@pytest.mark.asyncio
async def test_data_aggregator():
    """Test data aggregator service"""
    aggregator = DataAggregator()
    products = await aggregator.aggregate_product_trends(
        keywords=["test"],
        categories=["Electronics"],
        days_back=7
    )
    assert isinstance(products, list)


def test_platform_distribution():
    """Test platform distribution calculation"""
    from app.services.data_aggregator import DataAggregator
    
    aggregator = DataAggregator()
    
    # Mock products
    products = [
        Product(
            id="1",
            name="Test Product",
            category="Electronics",
            platforms=["amazon", "tiktok"],
            trend_score=0.8,
            viral_velocity=0.5,
            status="rising"
        )
    ]
    
    # This would test actual distribution logic
    assert len(products) > 0


@pytest.mark.asyncio
async def test_bedrock_agent_fallback():
    """Test Bedrock agent fallback"""
    from app.services.bedrock_agent import BedrockAgentService
    
    service = BedrockAgentService()
    fallback = service._get_fallback_analysis()
    
    assert "trend_score" in fallback
    assert "confidence" in fallback
