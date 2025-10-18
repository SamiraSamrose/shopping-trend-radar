"""
backend/app/utils/metrics.py
CloudWatch metrics and monitoring
"""

import boto3
from datetime import datetime
from typing import Dict, List
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class MetricsCollector:
    """Collect and send metrics to CloudWatch"""
    
    def __init__(self):
        self.cloudwatch = boto3.client(
            'cloudwatch',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.namespace = settings.CLOUDWATCH_NAMESPACE
    
    def record_api_call(
        self,
        endpoint: str,
        duration_ms: float,
        status_code: int
    ):
        """Record API call metrics"""
        if not settings.METRICS_ENABLED:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'APILatency',
                        'Dimensions': [
                            {'Name': 'Endpoint', 'Value': endpoint},
                            {'Name': 'StatusCode', 'Value': str(status_code)}
                        ],
                        'Value': duration_ms,
                        'Unit': 'Milliseconds',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'APICallCount',
                        'Dimensions': [
                            {'Name': 'Endpoint', 'Value': endpoint}
                        ],
                        'Value': 1,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Failed to record API metrics: {str(e)}")
    
    def record_trend_analysis(
        self,
        product_count: int,
        avg_score: float,
        processing_time_ms: float
    ):
        """Record trend analysis metrics"""
        if not settings.METRICS_ENABLED:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'ProductsAnalyzed',
                        'Value': product_count,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'AverageTrendScore',
                        'Value': avg_score,
                        'Unit': 'None',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'AnalysisProcessingTime',
                        'Value': processing_time_ms,
                        'Unit': 'Milliseconds',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Failed to record trend analysis metrics: {str(e)}")
    
    def record_platform_fetch(
        self,
        platform: str,
        item_count: int,
        success: bool
    ):
        """Record platform data fetch metrics"""
        if not settings.METRICS_ENABLED:
            return
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': 'PlatformFetchSuccess',
                        'Dimensions': [
                            {'Name': 'Platform', 'Value': platform}
                        ],
                        'Value': 1 if success else 0,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'ItemsFetched',
                        'Dimensions': [
                            {'Name': 'Platform', 'Value': platform}
                        ],
                        'Value': item_count,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Failed to record platform fetch metrics: {str(e)}")
