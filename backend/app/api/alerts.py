"""
backend/app/api/alerts.py
API endpoints for user alerts and notifications
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List
from datetime import datetime
from app.models.trends import Alert
from app.utils.logger import get_logger
import uuid

logger = get_logger(__name__)
router = APIRouter(prefix="/alerts", tags=["alerts"])

# In-memory storage (use database in production)
alerts_db = {}


@router.post("/", response_model=Alert)
async def create_alert(
    user_id: str = Body(...),
    keywords: List[str] = Body([]),
    categories: List[str] = Body([]),
    min_trend_score: float = Body(0.7),
    platforms: List[str] = Body([])
):
    """Create a new trend alert"""
    try:
        alert_id = str(uuid.uuid4())
        
        alert = Alert(
            id=alert_id,
            user_id=user_id,
            keywords=keywords,
            categories=categories,
            min_trend_score=min_trend_score,
            platforms=platforms,
            active=True
        )
        
        alerts_db[alert_id] = alert
        
        logger.info(f"Created alert {alert_id} for user {user_id}")
        return alert
    
    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[Alert])
async def get_user_alerts(user_id: str):
    """Get all alerts for a user"""
    try:
        user_alerts = [
            alert for alert in alerts_db.values()
            if alert.user_id == user_id
        ]
        
        return user_alerts
    
    except Exception as e:
        logger.error(f"Error fetching user alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{alert_id}", response_model=Alert)
async def update_alert(
    alert_id: str,
    keywords: List[str] = Body(None),
    categories: List[str] = Body(None),
    min_trend_score: float = Body(None),
    platforms: List[str] = Body(None),
    active: bool = Body(None)
):
    """Update an existing alert"""
    try:
        if alert_id not in alerts_db:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert = alerts_db[alert_id]
        
        if keywords is not None:
            alert.keywords = keywords
        if categories is not None:
            alert.categories = categories
        if min_trend_score is not None:
            alert.min_trend_score = min_trend_score
        if platforms is not None:
            alert.platforms = platforms
        if active is not None:
            alert.active = active
        
        alerts_db[alert_id] = alert
        
        logger.info(f"Updated alert {alert_id}")
        return alert
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert"""
    try:
        if alert_id not in alerts_db:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        del alerts_db[alert_id]
        
        logger.info(f"Deleted alert {alert_id}")
        return {"message": "Alert deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}/check")
async def check_alert(alert_id: str):
    """Check if alert conditions are met"""
    try:
        if alert_id not in alerts_db:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert = alerts_db[alert_id]
        
        if not alert.active:
            return {
                "alert_id": alert_id,
                "triggered": False,
                "reason": "Alert is inactive"
            }
        
        from app.services.data_aggregator import DataAggregator
        
        aggregator = DataAggregator()
        products = await aggregator.aggregate_product_trends(
            keywords=alert.keywords,
            categories=alert.categories,
            days_back=1
        )
        
        # Filter by alert criteria
        matching_products = [
            p for p in products
            if p.trend_score >= alert.min_trend_score
            and (not alert.platforms or any(pl in p.platforms for pl in alert.platforms))
        ]
        
        triggered = len(matching_products) > 0
        
        return {
            "alert_id": alert_id,
            "triggered": triggered,
            "matching_products": [p.dict() for p in matching_products[:5]],
            "checked_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
