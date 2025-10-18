"""
backend/app/config.py
Configuration management for Shopping Trend Radar Agent
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Shopping Trend Radar Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # AWS Bedrock
    BEDROCK_AGENT_ID: str = ""
    BEDROCK_AGENT_ALIAS_ID: str = ""
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # SageMaker
    SAGEMAKER_ENDPOINT_NAME: str = "trend-prediction-endpoint"
    SAGEMAKER_EXECUTION_ROLE: str = ""
    
    # Nova SDK
    NOVA_API_KEY: str = ""
    NOVA_API_URL: str = "https://api.nova.ai/v1"
    
    # Amazon Q
    AMAZON_Q_APP_ID: str = ""
    AMAZON_Q_USER_ID: str = ""
    
    # Strands SDK
    STRANDS_API_KEY: str = ""
    STRANDS_WORKSPACE_ID: str = ""
    
    # S3
    S3_BUCKET_NAME: str = "shopping-trend-radar-data"
    S3_DASHBOARD_PREFIX: str = "dashboards/"
    S3_DATA_PREFIX: str = "data/"
    
    # Lambda
    LAMBDA_DASHBOARD_FUNCTION: str = "trend-radar-dashboard-generator"
    LAMBDA_ANALYZER_FUNCTION: str = "trend-radar-analyzer"
    
    # External APIs
    YOUTUBE_API_KEY: str = ""
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    PINTEREST_ACCESS_TOKEN: str = ""
    ETSY_API_KEY: str = ""
    WALMART_API_KEY: str = ""
    EBAY_APP_ID: str = ""
    TARGET_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/trendradar"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    TREND_CACHE_TTL: int = 1800  # 30 minutes
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    METRICS_ENABLED: bool = True
    CLOUDWATCH_NAMESPACE: str = "TrendRadar"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Trend Analysis
    TREND_SCORE_THRESHOLD: float = 0.7
    VIRAL_VELOCITY_THRESHOLD: float = 0.8
    MIN_ENGAGEMENT_COUNT: int = 1000
    
    # Alert Settings
    ALERT_CHECK_INTERVAL: int = 300  # 5 minutes
    EMAIL_NOTIFICATIONS: bool = True
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Platform configuration
SUPPORTED_PLATFORMS = {
    "amazon": {
        "name": "Amazon",
        "api_endpoint": "https://webservices.amazon.com/paapi5",
        "weight": 0.25,
        "metrics": ["sales_rank", "reviews", "ratings", "best_seller_badge"]
    },
    "youtube": {
        "name": "YouTube",
        "api_endpoint": "https://www.googleapis.com/youtube/v3",
        "weight": 0.20,
        "metrics": ["views", "likes", "comments", "mentions"]
    },
    "tiktok": {
        "name": "TikTok",
        "api_endpoint": "https://open-api.tiktok.com",
        "weight": 0.20,
        "metrics": ["views", "likes", "shares", "hashtag_usage"]
    },
    "instagram": {
        "name": "Instagram",
        "api_endpoint": "https://graph.instagram.com",
        "weight": 0.15,
        "metrics": ["likes", "comments", "saves", "hashtag_usage"]
    },
    "meta": {
        "name": "Meta (Facebook)",
        "api_endpoint": "https://graph.facebook.com",
        "weight": 0.10,
        "metrics": ["likes", "shares", "comments", "engagement_rate"]
    },
    "pinterest": {
        "name": "Pinterest",
        "api_endpoint": "https://api.pinterest.com/v5",
        "weight": 0.03,
        "metrics": ["pins", "saves", "impressions"]
    },
    "etsy": {
        "name": "Etsy",
        "api_endpoint": "https://openapi.etsy.com/v3",
        "weight": 0.02,
        "metrics": ["favorites", "sales", "views"]
    },
    "walmart": {
        "name": "Walmart",
        "api_endpoint": "https://developer.api.walmart.com",
        "weight": 0.02,
        "metrics": ["sales_rank", "reviews", "stock_status"]
    },
    "ebay": {
        "name": "eBay",
        "api_endpoint": "https://api.ebay.com/buy/browse/v1",
        "weight": 0.02,
        "metrics": ["bids", "watchers", "sales"]
    },
    "target": {
        "name": "Target",
        "api_endpoint": "https://api.target.com",
        "weight": 0.01,
        "metrics": ["ratings", "reviews", "stock_status"]
    }
}

# Category configuration
PRODUCT_CATEGORIES = [
    "Electronics", "Fashion", "Beauty", "Home & Garden", 
    "Sports & Outdoors", "Toys & Games", "Health & Wellness",
    "Food & Beverage", "Pet Supplies", "Books & Media",
    "Automotive", "Office Supplies", "Baby & Kids"
]

# Event calendar
CALENDAR_EVENTS = {
    "01-01": {"name": "New Year's Day", "categories": ["Party Supplies", "Home Decor"]},
    "02-14": {"name": "Valentine's Day", "categories": ["Gifts", "Jewelry", "Flowers"]},
    "03-17": {"name": "St. Patrick's Day", "categories": ["Party Supplies", "Apparel"]},
    "05-12": {"name": "Mother's Day", "categories": ["Gifts", "Jewelry", "Flowers"]},
    "06-16": {"name": "Father's Day", "categories": ["Gifts", "Tools", "Electronics"]},
    "07-04": {"name": "Independence Day", "categories": ["Party Supplies", "BBQ"]},
    "10-31": {"name": "Halloween", "categories": ["Costumes", "Decorations", "Candy"]},
    "11-28": {"name": "Thanksgiving", "categories": ["Kitchen", "Home Decor"]},
    "11-29": {"name": "Black Friday", "categories": ["All"]},
    "12-02": {"name": "Cyber Monday", "categories": ["Electronics", "Fashion"]},
    "12-25": {"name": "Christmas", "categories": ["Gifts", "Decorations", "Toys"]},
}
