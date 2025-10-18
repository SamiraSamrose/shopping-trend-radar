"""
backend/lambda_functions/alert_notifier.py
Lambda function to check alerts and send notifications
"""

import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

alerts_table = os.environ.get('ALERTS_TABLE', 'TrendRadarAlerts')
products_table = os.environ.get('PRODUCTS_TABLE', 'TrendRadarProducts')
sender_email = os.environ.get('SENDER_EMAIL', 'noreply@trendradar.com')


def lambda_handler(event, context):
    """
    Check user alerts and send notifications
    Triggered periodically by EventBridge
    """
    try:
        # Get all active alerts
        alerts_tbl = dynamodb.Table(alerts_table)
        alerts_response = alerts_tbl.scan(
            FilterExpression='active = :active',
            ExpressionAttributeValues={':active': True}
        )
        alerts = alerts_response.get('Items', [])
        
        # Get current trending products
        products_tbl = dynamodb.Table(products_table)
        products_response = products_tbl.scan()
        products = products_response.get('Items', [])
        
        # Check each alert
        notifications_sent = 0
        for alert in alerts:
            matched = check_alert(alert, products)
            
            if matched:
                send_notification(alert, matched)
                notifications_sent += 1
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Alert check completed',
                'alerts_checked': len(alerts),
                'notifications_sent': notifications_sent
            })
        }
    
    except Exception as e:
        print(f"Error in alert notifier: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def check_alert(alert: dict, products: list) -> list:
    """Check if alert conditions are met"""
    
    matched_products = []
    
    keywords = alert.get('keywords', [])
    categories = alert.get('categories', [])
    min_score = alert.get('min_trend_score', 0.7)
    platforms = alert.get('platforms', [])
    
    for product in products:
        # Check trend score
        if product.get('trend_score', 0) < min_score:
            continue
        
        # Check keywords
        if keywords:
            product_text = f"{product.get('name', '')} {product.get('description', '')}".lower()
            if not any(kw.lower() in product_text for kw in keywords):
                continue
        
        # Check categories
        if categories and product.get('category') not in categories:
            continue
        
        # Check platforms
        if platforms:
            product_platforms = product.get('platforms', [])
            if not any(pl in product_platforms for pl in platforms):
                continue
        
        matched_products.append(product)
    
    return matched_products


def send_notification(alert: dict, matched_products: list):
    """Send email notification"""
    
    user_email = alert.get('user_email')
    if not user_email:
        print(f"No email for alert {alert.get('id')}")
        return
    
    # Build email content
    subject = f"Trend Alert: {len(matched_products)} products match your criteria"
    
    body_html = f"""
    <html>
    <head></head>
    <body>
        <h2>Shopping Trend Radar Alert</h2>
        <p>The following products match your alert criteria:</p>
        <ul>
    """
    
    for product in matched_products[:10]:  # Limit to 10
        body_html += f"""
            <li>
                <strong>{product.get('name')}</strong><br>
                Category: {product.get('category')}<br>
                Trend Score: {product.get('trend_score', 0):.2f}<br>
                Platforms: {', '.join(product.get('platforms', []))}<br>
            </li>
        """
    
    body_html += """
        </ul>
        <p>Visit the dashboard for more details.</p>
    </body>
    </html>
    """
    
    try:
        ses.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [user_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body_html}}
            }
        )
        print(f"Notification sent to {user_email}")
    
    except Exception as e:
        print(f"Error sending email: {str(e)}")
