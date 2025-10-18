"""
backend/lambda_functions/dashboard_generator.py
Lambda function to generate dashboards and store in S3
"""

import json
import boto3
import os
from datetime import datetime
from typing import Dict

s3_client = boto3.client('s3')
bucket_name = os.environ.get('S3_BUCKET_NAME', 'shopping-trend-radar-data')


def lambda_handler(event, context):
    """
    Lambda handler for dashboard generation
    Triggered periodically or on-demand
    """
    try:
        # Extract parameters
        user_type = event.get('user_type', 'merchant')
        categories = event.get('categories', [])
        
        # Generate dashboard data
        dashboard_data = generate_dashboard(user_type, categories)
        
        # Upload to S3
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        key = f"dashboards/{user_type}/{timestamp}.json"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(dashboard_data),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Dashboard generated successfully',
                's3_key': key,
                'timestamp': timestamp
            })
        }
    
    except Exception as e:
        print(f"Error generating dashboard: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def generate_dashboard(user_type: str, categories: list) -> Dict:
    """Generate dashboard data"""
    
    # This is a simplified version
    # In production, fetch real data from services
    
    dashboard = {
        'user_type': user_type,
        'generated_at': datetime.utcnow().isoformat(),
        'summary': {
            'total_products': 150,
            'trending_count': 45,
            'emerging_count': 12,
            'avg_trend_score': 0.68
        },
        'top_platforms': [
            {'name': 'TikTok', 'product_count': 78, 'growth': '+25%'},
            {'name': 'Instagram', 'product_count': 65, 'growth': '+18%'},
            {'name': 'YouTube', 'product_count': 52, 'growth': '+12%'}
        ],
        'top_categories': [
            {'name': 'Electronics', 'trend_score': 0.82},
            {'name': 'Fashion', 'trend_score': 0.75},
            {'name': 'Beauty', 'trend_score': 0.71}
        ]
    }
    
    if user_type == 'merchant':
        dashboard['merchant_insights'] = {
            'high_opportunity_products': 15,
            'low_competition_niches': 8,
            'recommended_inventory_value': '$25,000'
        }
    else:
        dashboard['consumer_insights'] = {
            'upcoming_events': 5,
            'price_drop_alerts': 12,
            'new_trending_items': 23
        }
    
    return dashboard
