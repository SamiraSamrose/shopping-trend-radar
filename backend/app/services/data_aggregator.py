"""
backend/app/services/data_aggregator.py
Aggregates data from all sources and calculates trend scores
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from app.config import get_settings, SUPPORTED_PLATFORMS
from app.models.trends import Product, PlatformMetrics, TrendStatus
from app.services.bedrock_agent import BedrockAgentService
from app.services.sagemaker_predictor import SageMakerPredictor
from app.services.nova_connector import NovaConnector
from app.services.strands_ingestion import StrandsIngestionService
from app.services.amazon_q_service import AmazonQService
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DataAggregator:
    """Aggregates and analyzes data from all platforms"""
    
    def __init__(self):
        self.bedrock = BedrockAgentService()
        self.sagemaker = SageMakerPredictor()
        self.amazon_q = AmazonQService()
    
    async def aggregate_product_trends(
        self,
        keywords: List[str],
        categories: List[str],
        days_back: int = 7
    ) -> List[Product]:
        """Aggregate trends from all platforms"""
        try:
            # Fetch data from all sources
            async with NovaConnector() as nova:
                hashtags = [f"#{kw.replace(' ', '')}" for kw in keywords]
                social_data = await nova.fetch_all_platforms(keywords, hashtags)
            
            strands = StrandsIngestionService()
            sales_data = await strands.ingest_all_platforms(days_back)
            
            # Process and merge data
            products = await self._process_all_data(
                social_data,
                sales_data,
                keywords,
                categories
            )
            
            # Calculate trend scores
            products = await self._calculate_trend_scores(products)
            
            # Get ML predictions
            products = await self._enrich_with_predictions(products)
            
            logger.info(f"Aggregated {len(products)} trending products")
            return products
        
        except Exception as e:
            logger.error(f"Error aggregating product trends: {str(e)}")
            return []
    
    async def _process_all_data(
        self,
        social_data: Dict,
        sales_data: Dict,
        keywords: List[str],
        categories: List[str]
    ) -> List[Product]:
        """Process and merge data from all sources"""
        product_map = defaultdict(lambda: {
            'platforms': set(),
            'metrics': {},
            'mentions': 0,
            'total_engagement': 0
        })
        
        # Process social media data
        for platform, items in social_data.items():
            for item in items:
                product_key = self._extract_product_identifier(item)
                
                if product_key:
                    product_map[product_key]['platforms'].add(platform)
                    product_map[product_key]['metrics'][platform] = self._extract_platform_metrics(item, platform)
                    product_map[product_key]['mentions'] += 1
                    product_map[product_key]['total_engagement'] += self._calculate_engagement(item)
        
        # Process sales data
        for platform, items in sales_data.items():
            for item in items:
                product_id = item.get('product_id')
                product_name = item.get('product_name')
                
                if product_id:
                    key = f"{platform}_{product_id}"
                    product_map[key]['platforms'].add(platform)
                    product_map[key]['sales_data'] = item
                    product_map[key]['product_name'] = product_name
        
        # Convert to Product objects
        products = []
        for key, data in product_map.items():
            if len(data['platforms']) > 0:  # At least one platform
                product = await self._create_product_from_data(key, data)
                if product:
                    products.append(product)
        
        return products
    
    async def _calculate_trend_scores(
        self,
        products: List[Product]
    ) -> List[Product]:
        """Calculate comprehensive trend scores"""
        for product in products:
            try:
                # Aggregate platform metrics
                total_engagement = 0
                total_views = 0
                total_growth = 0
                platform_count = len(product.platforms)
                
                for platform, metrics in product.platform_metrics.items():
                    weight = SUPPORTED_PLATFORMS.get(platform, {}).get('weight', 0.1)
                    
                    total_engagement += metrics.engagement_count * weight
                    total_views += metrics.views * weight
                    total_growth += metrics.growth_rate * weight
                
                # Calculate base score
                engagement_score = min(total_engagement / 100000, 1.0)  # Normalize
                view_score = min(total_views / 1000000, 1.0)
                growth_score = min(total_growth, 1.0)
                platform_score = min(platform_count / 5, 1.0)  # Max 5 platforms
                
                # Weighted average
                product.trend_score = (
                    engagement_score * 0.35 +
                    view_score * 0.25 +
                    growth_score * 0.30 +
                    platform_score * 0.10
                )
                
                # Calculate viral velocity
                days_active = (datetime.utcnow() - product.first_seen).days or 1
                product.viral_velocity = total_growth / days_active
                
                # Determine status
                product.status = self._determine_trend_status(
                    product.trend_score,
                    product.viral_velocity,
                    days_active
                )
                
            except Exception as e:
                logger.error(f"Error calculating trend score for {product.id}: {str(e)}")
                product.trend_score = 0.0
        
        return products
    
    async def _enrich_with_predictions(
        self,
        products: List[Product]
    ) -> List[Product]:
        """Enrich products with ML predictions"""
        try:
            # Prepare product data for batch prediction
            product_dicts = []
            for product in products:
                product_dict = {
                    'id': product.id,
                    'platforms': list(product.platforms),
                    'aggregated_metrics': self._aggregate_metrics(product),
                    'historical_scores': [product.trend_score]  # In production, use actual history
                }
                product_dicts.append(product_dict)
            
            # Get predictions
            predictions = await self.sagemaker.batch_predict(product_dicts)
            
            # Map predictions back to products
            prediction_map = {p['product_id']: p for p in predictions}
            
            for product in products:
                if product.id in prediction_map:
                    pred = prediction_map[product.id]
                    # Store prediction in product metadata
                    product.prediction = pred
            
        except Exception as e:
            logger.error(f"Error enriching with predictions: {str(e)}")
        
        return products
    
    def _extract_product_identifier(self, item: Dict) -> Optional[str]:
        """Extract product identifier from social media item"""
        # Use title, description, or hashtags to identify product
        text = item.get('title', '') or item.get('description', '') or item.get('caption', '')
        platform = item.get('platform')
        item_id = item.get('id')
        
        if text and item_id:
            # Create a normalized key
            return f"{platform}_{item_id}"
        
        return None
    
    def _extract_platform_metrics(self, item: Dict, platform: str) -> PlatformMetrics:
        """Extract metrics from platform item"""
        return PlatformMetrics(
            platform=platform,
            engagement_count=self._calculate_engagement(item),
            views=item.get('views', 0),
            likes=item.get('likes', 0),
            shares=item.get('shares', 0),
            comments=item.get('comments', 0),
            mentions=1,
            growth_rate=self._calculate_growth_rate(item),
            timestamp=datetime.utcnow()
        )
    
    def _calculate_engagement(self, item: Dict) -> int:
        """Calculate total engagement"""
        return (
            item.get('likes', 0) +
            item.get('comments', 0) +
            item.get('shares', 0) +
            item.get('saves', 0)
        )
    
    def _calculate_growth_rate(self, item: Dict) -> float:
        """Calculate growth rate (simplified)"""
        # In production, compare with historical data
        engagement = self._calculate_engagement(item)
        views = item.get('views', 1)
        
        return min(engagement / views, 1.0) if views > 0 else 0.0
    
    async def _create_product_from_data(
        self,
        key: str,
        data: Dict
    ) -> Optional[Product]:
        """Create Product object from aggregated data"""
        try:
            product_name = data.get('product_name') or self._extract_name_from_metrics(data)
            category = self._infer_category(product_name, data)
            
            # Build platform metrics dict
            platform_metrics = {}
            for platform, metrics in data.get('metrics', {}).items():
                if isinstance(metrics, PlatformMetrics):
                    platform_metrics[platform] = metrics
            
            product = Product(
                id=key,
                name=product_name,
                category=category,
                description=self._extract_description(data),
                platforms=list(data['platforms']),
                platform_metrics=platform_metrics,
                first_seen=datetime.utcnow() - timedelta(days=7),  # Placeholder
                last_updated=datetime.utcnow()
            )
            
            return product
        
        except Exception as e:
            logger.error(f"Error creating product from data: {str(e)}")
            return None
    
    def _extract_name_from_metrics(self, data: Dict) -> str:
        """Extract product name from metrics"""
        for metrics in data.get('metrics', {}).values():
            if hasattr(metrics, 'title'):
                return metrics.title
        
        return "Unknown Product"
    
    def _infer_category(self, product_name: str, data: Dict) -> str:
        """Infer product category"""
        # Simple keyword matching - in production use ML
        keywords = {
            'Electronics': ['phone', 'laptop', 'computer', 'tablet', 'headphone', 'camera'],
            'Fashion': ['dress', 'shirt', 'pants', 'shoe', 'jacket', 'accessory'],
            'Beauty': ['makeup', 'skincare', 'cosmetic', 'beauty', 'cream', 'serum'],
            'Home & Garden': ['furniture', 'decor', 'garden', 'kitchen', 'bedding'],
        }
        
        name_lower = product_name.lower()
        
        for category, words in keywords.items():
            if any(word in name_lower for word in words):
                return category
        
        return "General"
    
    def _extract_description(self, data: Dict) -> str:
        """Extract product description"""
        for metrics in data.get('metrics', {}).values():
            if hasattr(metrics, 'description'):
              return metrics.description
        
        sales_data = data.get('sales_data', {})
        if sales_data:
            return sales_data.get('description', '')
        
        return ""
    
    def _determine_trend_status(
        self,
        trend_score: float,
        viral_velocity: float,
        days_active: int
    ) -> TrendStatus:
        """Determine trend status based on metrics"""
        if viral_velocity > 0.8 and days_active < 3:
            return TrendStatus.EMERGING
        elif trend_score > 0.7 and viral_velocity > 0.5:
            return TrendStatus.RISING
        elif trend_score > 0.8 and viral_velocity < 0.3:
            return TrendStatus.PEAK
        elif trend_score < 0.5 and viral_velocity < 0:
            return TrendStatus.DECLINING
        else:
            return TrendStatus.STABLE
    
    def _aggregate_metrics(self, product: Product) -> Dict:
        """Aggregate all metrics for a product"""
        total_engagement = 0
        total_views = 0
        total_reviews = 0
        ratings = []
        
        for platform, metrics in product.platform_metrics.items():
            total_engagement += metrics.engagement_count
            total_views += metrics.views
        
        return {
            'total_engagement': total_engagement,
            'total_views': total_views,
            'total_reviews': total_reviews,
            'avg_rating': np.mean(ratings) if ratings else 0,
            'growth_rate': product.viral_velocity,
            'platform_count': len(product.platforms)
        }
    
    async def compare_product_prices(
        self,
        product_name: str,
        platforms: List[str]
    ) -> Dict:
        """Compare product prices across platforms"""
        # Implementation for price comparison
        comparisons = []
        
        for platform in platforms:
            # Fetch price data from each platform
            # This is a simplified version
            comparison = {
                'platform': platform,
                'price': 0.0,
                'availability': 'unknown',
                'shipping': 0.0,
                'reviews': 0,
                'rating': 0.0
            }
            comparisons.append(comparison)
        
        # Find best deal
        best_deal = min(comparisons, key=lambda x: x['price']) if comparisons else {}
        
        return {
            'product_name': product_name,
            'comparisons': comparisons,
            'best_deal': best_deal,
            'timestamp': datetime.utcnow().isoformat()
        }
