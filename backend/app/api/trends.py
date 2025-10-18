"""
backend/app/api/trends.py
API endpoints for trend data
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from app.models.trends import Product, TrendReport, TrendPrediction, TrendStatus, UserType
from app.services.data_aggregator import DataAggregator
from app.services.bedrock_agent import BedrockAgentService
from app.utils.logger import get_logger
from app.utils.metrics import MetricsCollector

logger = get_logger(__name__)
router = APIRouter(prefix="/trends", tags=["trends"])
metrics = MetricsCollector()


@router.get("/products", response_model=List[Product])
async def get_trending_products(
    categories: Optional[List[str]] = Query(None),
    platforms: Optional[List[str]] = Query(None),
    min_score: float = Query(0.5, ge=0, le=1),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[TrendStatus] = None
):
    """Get trending products with filters"""
    start_time = datetime.utcnow()
    
    try:
        aggregator = DataAggregator()
        
        # Default keywords if no categories provided
        keywords = categories or ["trending", "viral", "popular"]
        
        products = await aggregator.aggregate_product_trends(
            keywords=keywords,
            categories=categories or [],
            days_back=7
        )
        
        # Filter by criteria
        filtered = [
            p for p in products
            if p.trend_score >= min_score
            and (not platforms or any(pl in p.platforms for pl in platforms))
            and (not status or p.status == status)
        ]
        
        # Sort by trend score
        filtered.sort(key=lambda x: x.trend_score, reverse=True)
        
        # Limit results
        result = filtered[:limit]
        
        # Record metrics
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        avg_score = sum(p.trend_score for p in result) / len(result) if result else 0
        metrics.record_trend_analysis(len(result), avg_score, duration)
        
        return result
    
    except Exception as e:
        logger.error(f"Error fetching trending products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}", response_model=Product)
async def get_product_details(product_id: str):
    """Get detailed information about a specific product"""
    try:
        # In production, fetch from database
        aggregator = DataAggregator()
        products = await aggregator.aggregate_product_trends(
            keywords=[product_id],
            categories=[],
            days_back=7
        )
        
        product = next((p for p in products if p.id == product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{product_id}", response_model=TrendPrediction)
async def get_trend_prediction(product_id: str):
    """Get ML prediction for product trend"""
    try:
        bedrock = BedrockAgentService()
        
        # Fetch historical data (simplified)
        historical_data = []  # In production, fetch from database
        
        prediction = await bedrock.predict_trend_trajectory(
            product_id=product_id,
            historical_data=historical_data
        )
        
        return TrendPrediction(
            product_id=product_id,
            predicted_peak_date=prediction.get('predicted_peak_date'),
            confidence_score=prediction.get('confidence_score', 0),
            duration_days=prediction.get('duration_days'),
            max_predicted_score=prediction.get('max_predicted_score', 0),
            recommendation=prediction.get('recommendation', ''),
            factors=prediction.get('factors', {})
        )
    
    except Exception as e:
        logger.error(f"Error generating prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report", response_model=TrendReport)
async def generate_trend_report(
    user_type: UserType = Query(...),
    categories: Optional[List[str]] = Query(None),
    days_back: int = Query(7, ge=1, le=30)
):
    """Generate comprehensive trend report"""
    try:
        aggregator = DataAggregator()
        
        keywords = categories or ["trending", "popular", "viral"]
        
        products = await aggregator.aggregate_product_trends(
            keywords=keywords,
            categories=categories or [],
            days_back=days_back
        )
        
        # Sort products
        top_trending = sorted(products, key=lambda x: x.trend_score, reverse=True)[:20]
        emerging_trends = [p for p in products if p.status == TrendStatus.EMERGING][:10]
        
        # Category breakdown
        category_breakdown = {}
        for product in products:
            category_breakdown[product.category] = category_breakdown.get(product.category, 0) + 1
        
        # Platform analysis
        platform_analysis = {}
        for platform in ['amazon', 'youtube', 'tiktok', 'instagram', 'meta']:
            platform_products = [p for p in products if platform in p.platforms]
            platform_analysis[platform] = {
                'product_count': len(platform_products),
                'avg_score': sum(p.trend_score for p in platform_products) / len(platform_products) if platform_products else 0
            }
        
        # Generate insights
        insights = await _generate_insights(products, user_type)
        
        report = TrendReport(
            report_id=f"report_{datetime.utcnow().timestamp()}",
            user_type=user_type,
            top_trending=top_trending,
            emerging_trends=emerging_trends,
            category_breakdown=category_breakdown,
            platform_analysis=platform_analysis,
            predictions=[],
            upcoming_events=[],
            insights=insights
        )
        
        return report
    
    except Exception as e:
        logger.error(f"Error generating trend report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_trending_categories():
    """Get trending product categories"""
    try:
        aggregator = DataAggregator()
        
        products = await aggregator.aggregate_product_trends(
            keywords=["trending"],
            categories=[],
            days_back=7
        )
        
        # Count by category
        category_counts = {}
        category_scores = {}
        
        for product in products:
            cat = product.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
            category_scores[cat] = category_scores.get(cat, []) + [product.trend_score]
        
        # Calculate average scores
        results = []
        for category, count in category_counts.items():
            avg_score = sum(category_scores[category]) / len(category_scores[category])
            results.append({
                'category': category,
                'product_count': count,
                'avg_trend_score': avg_score,
                'momentum': 'rising' if avg_score > 0.7 else 'stable'
            })
        
        # Sort by score
        results.sort(key=lambda x: x['avg_trend_score'], reverse=True)
        
        return results
    
    except Exception as e:
        logger.error(f"Error fetching trending categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_insights(products: List[Product], user_type: UserType) -> List[str]:
    """Generate insights based on user type"""
    insights = []
    
    if not products:
        return ["No trending products found in the specified criteria."]
    
    # General insights
    avg_score = sum(p.trend_score for p in products) / len(products)
    insights.append(f"Average trend score across {len(products)} products: {avg_score:.2f}")
    
    # Platform insights
    platform_counts = {}
    for product in products:
        for platform in product.platforms:
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    top_platform = max(platform_counts.items(), key=lambda x: x[1])[0] if platform_counts else None
    if top_platform:
        insights.append(f"{top_platform.capitalize()} has the most trending products ({platform_counts[top_platform]} products)")
    
    # User-specific insights
    if user_type == UserType.MERCHANT:
        emerging = [p for p in products if p.status == TrendStatus.EMERGING]
        if emerging:
            insights.append(f"{len(emerging)} emerging trends detected - opportunity for early positioning")
        
        high_velocity = [p for p in products if p.viral_velocity > 0.7]
        if high_velocity:
            insights.append(f"{len(high_velocity)} products showing high viral velocity - act quickly")
    
    else:  # Consumer
        peak_products = [p for p in products if p.status == TrendStatus.PEAK]
        if peak_products:
            insights.append(f"{len(peak_products)} products at peak popularity - high social proof")
        
        insights.append("Check product comparisons for best deals across platforms")
    
    return insights
