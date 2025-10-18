"""
backend/app/api/products.py
API endpoints for product operations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.trends import ProductComparison, EventRecommendation, MerchantInsight, ConsumerInsight
from app.services.data_aggregator import DataAggregator
from app.services.amazon_q_service import AmazonQService
from app.config import CALENDAR_EVENTS
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/products", tags=["products"])


@router.get("/compare/{product_name}", response_model=ProductComparison)
async def compare_product_prices(
    product_name: str,
    platforms: Optional[List[str]] = Query(None)
):
    """Compare product prices across platforms"""
    try:
        aggregator = DataAggregator()
        
        # Default to all e-commerce platforms
        if not platforms:
            platforms = ['amazon', 'walmart', 'ebay', 'etsy', 'target']
        
        comparison = await aggregator.compare_product_prices(
            product_name=product_name,
            platforms=platforms
        )
        
        return ProductComparison(**comparison)
    
    except Exception as e:
        logger.error(f"Error comparing product prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events", response_model=List[EventRecommendation])
async def get_event_recommendations(
    days_ahead: int = Query(30, ge=1, le=90)
):
    """Get product recommendations for upcoming events"""
    try:
        today = datetime.utcnow()
        recommendations = []
        
        for date_str, event_info in CALENDAR_EVENTS.items():
            month, day = map(int, date_str.split('-'))
            event_date = datetime(today.year, month, day)
            
            # If event already passed this year, check next year
            if event_date < today:
                event_date = datetime(today.year + 1, month, day)
            
            days_until = (event_date - today).days
            
            if 0 <= days_until <= days_ahead:
                # Fetch trending products for this event
                aggregator = DataAggregator()
                products = await aggregator.aggregate_product_trends(
                    keywords=[event_info['name']],
                    categories=event_info.get('categories', []),
                    days_back=14
                )
                
                # Sort by trend score
                products.sort(key=lambda x: x.trend_score, reverse=True)
                top_products = products[:10]
                
                # Determine urgency
                if days_until < 7:
                    urgency = "high"
                elif days_until < 14:
                    urgency = "medium"
                else:
                    urgency = "low"
                
                recommendation = EventRecommendation(
                    event_name=event_info['name'],
                    event_date=event_date,
                    days_until_event=days_until,
                    recommended_products=top_products,
                    best_platforms=[],  # TODO: Calculate best platforms
                    price_trends={},  # TODO: Calculate price trends
                    buying_urgency=urgency
                )
                
                recommendations.append(recommendation)
        
        # Sort by date
        recommendations.sort(key=lambda x: x.event_date)
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error getting event recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/merchant-insights/{product_id}", response_model=MerchantInsight)
async def get_merchant_insights(product_id: str):
    """Get merchant-specific insights for a product"""
    try:
        aggregator = DataAggregator()
        amazon_q = AmazonQService()
        
        # Fetch product details
        products = await aggregator.aggregate_product_trends(
            keywords=[product_id],
            categories=[],
            days_back=7
        )
        
        product = next((p for p in products if p.id == product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Calculate competition level
        competition_level = "high" if product.trend_score > 0.8 else "medium" if product.trend_score > 0.5 else "low"
        
        # Calculate profit potential
        profit_potential = product.trend_score * product.viral_velocity * 100
        
        # Generate sourcing recommendations
        sourcing_recs = [
            {
                'supplier': 'Alibaba',
                'estimated_cost': product.price * 0.3 if product.price else 0,
                'lead_time_days': 30,
                'min_order_quantity': 100
            },
            {
                'supplier': 'Local Wholesaler',
                'estimated_cost': product.price * 0.5 if product.price else 0,
                'lead_time_days': 7,
                'min_order_quantity': 20
            }
        ]
        
        # Inventory recommendation
        if product.status.value == 'emerging':
            stock_recommendation = 'moderate'
            suggested_units = 50
        elif product.status.value == 'rising':
            stock_recommendation = 'high'
            suggested_units = 200
        elif product.status.value == 'peak':
            stock_recommendation = 'very_high'
            suggested_units = 500
        else:
            stock_recommendation = 'low'
            suggested_units = 20
        
        inventory_rec = {
            'recommendation': stock_recommendation,
            'suggested_units': suggested_units,
            'reorder_point': suggested_units * 0.3
        }
        
        # Ad targeting suggestions
        ad_suggestions = []
        for platform in product.platforms:
            ad_suggestions.append({
                'platform': platform,
                'target_audience': f'{product.category} enthusiasts',
                'suggested_budget': '$50-100/day',
                'keywords': [product.name, product.category, 'trending']
            })
        
        # Niche opportunities
        niche_opportunities = [
            f"Eco-friendly version of {product.category}",
            f"Premium {product.category} for luxury market",
            f"Budget-friendly alternative"
        ]
        
        insight = MerchantInsight(
            product_id=product_id,
            sourcing_recommendations=sourcing_recs,
            competition_level=competition_level,
            profit_potential=profit_potential,
            inventory_recommendation=inventory_rec,
            ad_targeting_suggestions=ad_suggestions,
            niche_opportunities=niche_opportunities
        )
        
        return insight
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating merchant insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consumer-insights/{product_id}", response_model=ConsumerInsight)
async def get_consumer_insights(product_id: str):
    """Get consumer-specific insights for a product"""
    try:
        aggregator = DataAggregator()
        
        # Fetch product details
        products = await aggregator.aggregate_product_trends(
            keywords=[product_id],
            categories=[],
            days_back=7
        )
        
        product = next((p for p in products if p.id == product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Popularity score
        popularity_score = product.trend_score
        
        # Price trend (simplified)
        price_trend = "stable"
        if product.viral_velocity > 0.5:
            price_trend = "increasing"
        elif product.viral_velocity < -0.3:
            price_trend = "decreasing"
        
        # Best time to buy
        if product.status.value == 'emerging':
            best_time = "Buy now - price may increase as popularity grows"
        elif product.status.value == 'peak':
            best_time = "Wait - price may drop soon as trend peaks"
        elif product.status.value == 'declining':
            best_time = "Good time to buy - prices dropping"
        else:
            best_time = "Stable - buy when convenient"
        
        # Social proof
        total_engagement = sum(
            m.engagement_count for m in product.platform_metrics.values()
        )
        
        social_proof = {
            'total_mentions': len(product.platforms),
            'total_engagement': total_engagement,
            'platforms': list(product.platforms),
            'viral_status': product.status.value
        }
        
        # Gift suitability
        gift_suitability = {
            'suitable_for': ['birthdays', 'holidays'] if product.trend_score > 0.6 else [],
            'age_groups': ['18-35'] if 'tech' in product.category.lower() else ['all'],
            'occasions': ['casual', 'special'] if product.trend_score > 0.7 else ['casual']
        }
        
        # Find similar trending products
        similar_products = [
            p.id for p in products
            if p.category == product.category and p.id != product_id
        ][:5]
        
        insight = ConsumerInsight(
            product_id=product_id,
            popularity_score=popularity_score,
            price_trend=price_trend,
            best_time_to_buy=best_time,
            similar_trending_products=similar_products,
            social_proof=social_proof,
            gift_suitability=gift_suitability
        )
        
        return insight
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating consumer insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance-check")
async def check_product_compliance(
    product_name: str,
    category: str,
    description: Optional[str] = None
):
    """Check product compliance across platforms"""
    try:
        amazon_q = AmazonQService()
        
        product_data = {
            'name': product_name,
            'category': category,
            'description': description or ''
        }
        
        compliance = await amazon_q.query_compliance_check(product_data)
        
        return compliance
    
    except Exception as e:
        logger.error(f"Error checking compliance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
