"""
scripts/seed_data.py
Seed database with sample data for testing
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from datetime import datetime, timedelta
import random
from app.models.trends import Product, TrendStatus, PlatformMetrics

# Sample product data
SAMPLE_PRODUCTS = [
    {
        "name": "Wireless Bluetooth Earbuds",
        "category": "Electronics",
        "platforms": ["amazon", "tiktok", "youtube"],
        "base_score": 0.85
    },
    {
        "name": "Smart Fitness Tracker",
        "category": "Electronics",
        "platforms": ["amazon", "instagram", "youtube"],
        "base_score": 0.78
    },
    {
        "name": "LED Strip Lights",
        "category": "Home & Garden",
        "platforms": ["tiktok", "instagram", "pinterest"],
        "base_score": 0.72
    },
    {
        "name": "Eco-Friendly Water Bottle",
        "category": "Sports & Outdoors",
        "platforms": ["amazon", "instagram", "etsy"],
        "base_score": 0.68
    },
    {
        "name": "Portable Phone Charger",
        "category": "Electronics",
        "platforms": ["amazon", "walmart", "ebay"],
        "base_score": 0.81
    },
    {
        "name": "Yoga Mat with Alignment Lines",
        "category": "Sports & Outdoors",
        "platforms": ["amazon", "instagram", "youtube"],
        "base_score": 0.75
    },
    {
        "name": "Instant Pot Air Fryer",
        "category": "Home & Garden",
        "platforms": ["amazon", "youtube", "meta"],
        "base_score": 0.88
    },
    {
        "name": "Minimalist Wallet",
        "category": "Fashion",
        "platforms": ["etsy", "instagram", "tiktok"],
        "base_score": 0.70
    },
    {
        "name": "Gaming Mouse RGB",
        "category": "Electronics",
        "platforms": ["amazon", "youtube", "tiktok"],
        "base_score": 0.82
    },
    {
        "name": "Skincare Serum Set",
        "category": "Beauty",
        "platforms": ["amazon", "instagram", "tiktok"],
        "base_score": 0.79
    }
]


async def seed_database():
    """Seed database with sample products"""
    print("🌱 Seeding database with sample data...")
    
    products = []
    
    for i, sample in enumerate(SAMPLE_PRODUCTS):
        # Generate platform metrics
        platform_metrics = {}
        for platform in sample["platforms"]:
            metrics = PlatformMetrics(
                platform=platform,
                engagement_count=random.randint(10000, 500000),
                views=random.randint(100000, 5000000),
                likes=random.randint(5000, 250000),
                shares=random.randint(1000, 50000),
                comments=random.randint(500, 25000),
                mentions=random.randint(100, 5000),
                growth_rate=random.uniform(0.1, 0.9),
                timestamp=datetime.utcnow()
            )
            platform_metrics[platform] = metrics
        
        # Determine status
        score = sample["base_score"] + random.uniform(-0.1, 0.1)
        velocity = random.uniform(0.3, 0.9)
        days_active = random.randint(1, 30)
        
        if velocity > 0.8 and days_active < 5:
            status = TrendStatus.EMERGING
        elif score > 0.75 and velocity > 0.5:
            status = TrendStatus.RISING
        elif score > 0.85:
            status = TrendStatus.PEAK
        elif score < 0.6:
            status = TrendStatus.DECLINING
        else:
            status = TrendStatus.STABLE
        
        # Create product
        product = Product(
            id=f"product_{i+1}",
            name=sample["name"],
            category=sample["category"],
            description=f"High-quality {sample['name'].lower()} with excellent reviews",
            price=round(random.uniform(19.99, 199.99), 2),
            platforms=sample["platforms"],
            trend_score=round(score, 2),
            viral_velocity=round(velocity, 2),
            status=status,
            platform_metrics=platform_metrics,
            first_seen=datetime.utcnow() - timedelta(days=days_active),
            last_updated=datetime.utcnow()
        )
        
        products.append(product)
        print(f"  ✓ Created: {product.name} (Score: {product.trend_score}, Status: {product.status.value})")
    
    # In production, save to database here
    # For demo, just print summary
    print(f"\n✅ Successfully seeded {len(products)} products")
    print(f"   - Emerging: {sum(1 for p in products if p.status == TrendStatus.EMERGING)}")
    print(f"   - Rising: {sum(1 for p in products if p.status == TrendStatus.RISING)}")
    print(f"   - Peak: {sum(1 for p in products if p.status == TrendStatus.PEAK)}")
    print(f"   - Stable: {sum(1 for p in products if p.status == TrendStatus.STABLE)}")
    print(f"   - Declining: {sum(1 for p in products if p.status == TrendStatus.DECLINING)}")


if __name__ == "__main__":
    asyncio.run(seed_database())
