"""
backend/lambda_functions/trend_analyzer.py
Lambda function for periodic trend analysis
"""

import json
import boto3
import os
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

table_name = os.environ.get('DYNAMODB_TABLE', 'TrendRadarProducts')
sns_topic = os.environ.get('SNS_TOPIC_ARN', '')


def lambda_handler(event, context):
    """
    Analyze trends and update database
    Triggered by EventBridge on schedule
    """
    try:
        # Get products from DynamoDB
        table = dynamodb.Table(table_name)
        response = table.scan()
        products = response.get('Items', [])
        
        # Analyze trends
        analysis_results = analyze_trends(products)
        
        # Update database with new scores
        update_products(table, analysis_results)
        
        # Send notifications for significant changes
        if analysis_results['significant_changes']:
            send_notifications(analysis_results['significant_changes'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Trend analysis completed',
                'products_analyzed': len(products),
                'significant_changes': len(analysis_results['significant_changes'])
            })
        }
    
    except Exception as e:
        print(f"Error in trend analysis: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def analyze_trends(products: list) -> dict:
    """Analyze product trends"""
    
    significant_changes = []
    
    for product in products:
        old_score = product.get('trend_score', 0)
        
        # Calculate new score (simplified)
        # In production, use actual metrics
        new_score = calculate_new_score(product)
        
        score_change = new_score - old_score
        
        # Check for significant change (>20% change)
        if abs(score_change) > 0.2:
            significant_changes.append({
                'product_id': product.get('id'),
                'product_name': product.get('name'),
                'old_score': old_score,
                'new_score': new_score,
                'change': score_change
            })
        
        product['trend_score'] = new_score
        product['last_analyzed'] = datetime.utcnow().isoformat()
    
    return {
        'products': products,
        'significant_changes': significant_changes
    }


def calculate_new_score(product: dict) -> float:
    """Calculate new trend score"""
    # Simplified calculation
    # In production, aggregate from all platforms
    
    base_score = product.get('trend_score', 0.5)
    
    # Add some variation
    import random
    variation = random.uniform(-0.1, 0.1)
    
    new_score = max(0, min(1, base_score + variation))
    
    return round(new_score, 3)


def update_products(table, analysis_results: dict):
    """Update products in DynamoDB"""
    
    for product in analysis_results['products']:
        try:
            table.put_item(Item=product)
        except Exception as e:
            print(f"Error updating product {product.get('id')}: {str(e)}")


def send_notifications(changes: list):
    """Send SNS notifications for significant changes"""
    
    if not sns_topic or not changes:
        return
    
    message = "Significant trend changes detected:\n\n"
    
    for change in changes[:10]:  # Limit to 10
        message += f"- {change['product_name']}: {change['old_score']:.2f} → {change['new_score']:.2f}\n"
    
    try:
        sns.publish(
            TopicArn=sns_topic,
            Subject="Shopping Trend Radar - Significant Changes",
            Message=message
        )
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
