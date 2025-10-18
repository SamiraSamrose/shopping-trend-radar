"""
backend/app/models/__init__.py
Data models package
"""

from .trends import (
    Product,
    TrendStatus,
    UserType,
    PlatformMetrics,
    TrendPrediction,
    ProductComparison,
    Alert,
    EventRecommendation,
    TrendReport,
    MerchantInsight,
    ConsumerInsight
)
from .users import User, UserPreferences

__all__ = [
    "Product",
    "TrendStatus",
    "UserType",
    "PlatformMetrics",
    "TrendPrediction",
    "ProductComparison",
    "Alert",
    "EventRecommendation",
    "TrendReport",
    "MerchantInsight",
    "ConsumerInsight",
    "User",
    "UserPreferences"
]
