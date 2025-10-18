"""
backend/app/services/sagemaker_predictor.py
SageMaker ML model for trend prediction
"""

import json
import boto3
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SageMakerPredictor:
    """Service for SageMaker trend predictions"""
    
    def __init__(self):
        self.sagemaker_runtime = boto3.client(
            'sagemaker-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.endpoint_name = settings.SAGEMAKER_ENDPOINT_NAME
    
    async def predict_trend(
        self,
        features: Dict,
        time_series_data: List[float]
    ) -> Dict:
        """
        Predict trend using SageMaker endpoint
        """
        try:
            # Prepare input data
            input_data = self._prepare_input(features, time_series_data)
            
            # Invoke endpoint
            response = self.sagemaker_runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(input_data)
            )
            
            # Parse prediction
            result = json.loads(response['Body'].read().decode())
            prediction = self._parse_prediction(result)
            
            logger.info(f"SageMaker prediction completed: {prediction.get('trend_direction')}")
            return prediction
            
        except Exception as e:
            logger.error(f"SageMaker prediction error: {str(e)}")
            return self._get_fallback_prediction()
    
    async def batch_predict(
        self,
        products: List[Dict]
    ) -> List[Dict]:
        """
        Batch prediction for multiple products
        """
        predictions = []
        
        for product in products:
            try:
                features = self._extract_features(product)
                time_series = product.get('historical_scores', [])
                
                prediction = await self.predict_trend(features, time_series)
                prediction['product_id'] = product.get('id')
                predictions.append(prediction)
                
            except Exception as e:
                logger.error(f"Batch prediction error for {product.get('id')}: {str(e)}")
                continue
        
        return predictions
    
    async def forecast_demand(
        self,
        product_id: str,
        historical_sales: List[int],
        days_ahead: int = 30
    ) -> Dict:
        """
        Forecast demand for inventory planning
        """
        try:
            input_data = {
                'product_id': product_id,
                'historical_sales': historical_sales,
                'forecast_horizon': days_ahead
            }
            
            response = self.sagemaker_runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(input_data)
            )
            
            result = json.loads(response['Body'].read().decode())
            
            return {
                'product_id': product_id,
                'forecast': result.get('predictions', []),
                'confidence_intervals': result.get('confidence_intervals', {}),
                'recommended_stock': self._calculate_stock_recommendation(result),
                'peak_demand_date': self._find_peak_date(result.get('predictions', []))
            }
            
        except Exception as e:
            logger.error(f"Demand forecast error: {str(e)}")
            return {'error': str(e)}
    
    def _prepare_input(
        self,
        features: Dict,
        time_series: List[float]
    ) -> Dict:
        """Prepare input for SageMaker"""
        return {
            'features': {
                'engagement_rate': features.get('engagement_rate', 0),
                'growth_rate': features.get('growth_rate', 0),
                'platform_count': features.get('platform_count', 0),
                'price': features.get('price', 0),
                'review_count': features.get('review_count', 0),
                'rating': features.get('rating', 0),
                'days_trending': features.get('days_trending', 0)
            },
            'time_series': time_series[-30:] if len(time_series) > 30 else time_series,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _extract_features(self, product: Dict) -> Dict:
        """Extract features from product data"""
        metrics = product.get('aggregated_metrics', {})
        
        return {
            'engagement_rate': metrics.get('total_engagement', 0) / max(metrics.get('total_views', 1), 1),
            'growth_rate': metrics.get('growth_rate', 0),
            'platform_count': len(product.get('platforms', [])),
            'price': product.get('price', 0),
            'review_count': metrics.get('total_reviews', 0),
            'rating': metrics.get('avg_rating', 0),
            'days_trending': (datetime.utcnow() - datetime.fromisoformat(
                product.get('first_seen', datetime.utcnow().isoformat())
            )).days
        }
    
    def _parse_prediction(self, result: Dict) -> Dict:
        """Parse SageMaker prediction result"""
        predictions = result.get('predictions', [0.5])[0]
        
        if isinstance(predictions, list):
            trend_score = predictions[0]
        else:
            trend_score = predictions
        
        return {
            'trend_score': float(trend_score),
            'trend_direction': self._determine_direction(trend_score),
            'confidence': result.get('confidence', 0.5),
            'predicted_at': datetime.utcnow().isoformat(),
            'model_version': result.get('model_version', '1.0')
        }
    
    def _determine_direction(self, score: float) -> str:
        """Determine trend direction from score"""
        if score > 0.8:
            return 'strongly_rising'
        elif score > 0.6:
            return 'rising'
        elif score > 0.4:
            return 'stable'
        elif score > 0.2:
            return 'declining'
        else:
            return 'strongly_declining'
    
    def _calculate_stock_recommendation(self, forecast_result: Dict) -> int:
        """Calculate recommended stock based on forecast"""
        predictions = forecast_result.get('predictions', [])
        if not predictions:
            return 0
        
        avg_demand = np.mean(predictions)
        peak_demand = max(predictions)
        
        # Safety stock = 1.5 * average + buffer for peak
        recommended = int(avg_demand * 1.5 + (peak_demand - avg_demand) * 0.5)
        
        return max(recommended, 0)
    
    def _find_peak_date(self, predictions: List[float]) -> str:
        """Find predicted peak demand date"""
        if not predictions:
            return None
        
        peak_index = predictions.index(max(predictions))
        peak_date = datetime.utcnow() + timedelta(days=peak_index)
        
        return peak_date.isoformat()
    
    def _get_fallback_prediction(self) -> Dict:
        """Fallback when prediction fails"""
        return {
            'trend_score': 0.5,
            'trend_direction': 'stable',
            'confidence': 0.0,
            'predicted_at': datetime.utcnow().isoformat(),
            'error': 'Prediction service unavailable'
        }
