"""
backend/app/services/strands_ingestion.py
Strands SDK integration for sales data ingestion
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class StrandsIngestionService:
    """Service for ingesting sales data via Strands SDK"""
    
    def __init__(self):
        self.api_key = settings.STRANDS_API_KEY
        self.workspace_id = settings.STRANDS_WORKSPACE_ID
        self.base_url = "https://api.strands.com/v1"
    
    async def ingest_amazon_sales(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Ingest Amazon sales data"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'workspace_id': self.workspace_id,
                    'source': 'amazon',
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'metrics': ['sales', 'revenue', 'units_sold', 'views']
                }
                
                async with session.post(
                    f'{self.base_url}/data/ingest',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_sales_data(data)
                    else:
                        logger.error(f"Amazon sales ingestion failed: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error ingesting Amazon sales: {str(e)}")
            return []
    
    async def ingest_walmart_sales(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Ingest Walmart sales data"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'WM_SVC.NAME': 'Walmart Marketplace',
                    'WM_QOS.CORRELATION_ID': str(datetime.utcnow().timestamp()),
                    'WM_SEC.ACCESS_TOKEN': settings.WALMART_API_KEY
                }
                
                params = {
                    'startDate': start_date.strftime('%Y-%m-%d'),
                    'endDate': end_date.strftime('%Y-%m-%d')
                }
                
                async with session.get(
                    'https://marketplace.walmartapis.com/v3/insights/items',
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_walmart_data(data)
                    return []
        
        except Exception as e:
            logger.error(f"Error ingesting Walmart sales: {str(e)}")
            return []
    
    async def ingest_ebay_sales(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Ingest eBay sales data"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {settings.EBAY_APP_ID}',
                    'Content-Type': 'application/json'
                }
                
                params = {
                    'filter': f'lastModifiedDate:[{start_date.isoformat()}..{end_date.isoformat()}]',
                    'fieldgroups': 'COMPACT'
                }
                
                async with session.get(
                    'https://api.ebay.com/sell/inventory/v1/inventory_item',
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_ebay_data(data)
                    return []
        
        except Exception as e:
            logger.error(f"Error ingesting eBay sales: {str(e)}")
            return []
    
    async def ingest_etsy_sales(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Ingest Etsy sales data"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': settings.ETSY_API_KEY,
                    'Content-Type': 'application/json'
                }
                
                params = {
                    'min_created': int(start_date.timestamp()),
                    'max_created': int(end_date.timestamp()),
                    'limit': 100
                }
                
                async with session.get(
                    'https://openapi.etsy.com/v3/application/shops/receipts',
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_etsy_data(data)
                    return []
        
        except Exception as e:
            logger.error(f"Error ingesting Etsy sales: {str(e)}")
            return []
    
    async def ingest_target_sales(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Ingest Target sales data"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {settings.TARGET_API_KEY}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
                
                async with session.post(
                    'https://api.target.com/products/v1/sales',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_target_data(data)
                    return []
        
        except Exception as e:
            logger.error(f"Error ingesting Target sales: {str(e)}")
            return []
    
    async def ingest_all_platforms(
        self,
        days_back: int = 7
    ) -> Dict[str, List[Dict]]:
        """Ingest sales data from all platforms"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        tasks = [
            self.ingest_amazon_sales(start_date, end_date),
            self.ingest_walmart_sales(start_date, end_date),
            self.ingest_ebay_sales(start_date, end_date),
            self.ingest_etsy_sales(start_date, end_date),
            self.ingest_target_sales(start_date, end_date)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'amazon': results[0] if not isinstance(results[0], Exception) else [],
            'walmart': results[1] if not isinstance(results[1], Exception) else [],
            'ebay': results[2] if not isinstance(results[2], Exception) else [],
            'etsy': results[3] if not isinstance(results[3], Exception) else [],
            'target': results[4] if not isinstance(results[4], Exception) else []
        }
    
    def _parse_sales_data(self, data: Dict) -> List[Dict]:
        """Parse Strands API response"""
        results = []
        
        for item in data.get('items', []):
            results.append({
                'product_id': item.get('product_id'),
                'product_name': item.get('name'),
                'sales': item.get('sales', 0),
                'revenue': item.get('revenue', 0),
                'units_sold': item.get('units_sold', 0),
                'views': item.get('views', 0),
                'conversion_rate': item.get('conversion_rate', 0),
                'timestamp': item.get('timestamp')
            })
        
        return results
    
    def _parse_walmart_data(self, data: Dict) -> List[Dict]:
        """Parse Walmart API response"""
        results = []
        
        for item in data.get('elements', []):
            results.append({
                'product_id': item.get('itemId'),
                'product_name': item.get('productName'),
                'sales': item.get('orderedUnits', 0),
                'revenue': item.get('orderedRevenue', 0),
                'views': item.get('pageViews', 0),
                'platform': 'walmart',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return results
    
    def _parse_ebay_data(self, data: Dict) -> List[Dict]:
        """Parse eBay API response"""
        results = []
        
        for item in data.get('inventoryItems', []):
            results.append({
                'product_id': item.get('sku'),
                'product_name': item.get('product', {}).get('title'),
                'available_quantity': item.get('availability', {}).get('shipToLocationAvailability', {}).get('quantity', 0),
                'price': item.get('product', {}).get('aspects', {}).get('price', 0),
                'platform': 'ebay',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return results
    
    def _parse_etsy_data(self, data: Dict) -> List[Dict]:
        """Parse Etsy API response"""
        results = []
        
        for receipt in data.get('results', []):
            for transaction in receipt.get('transactions', []):
                results.append({
                    'product_id': transaction.get('listing_id'),
                    'product_name': transaction.get('title'),
                    'sales': transaction.get('quantity', 0),
                    'revenue': float(transaction.get('price', {}).get('amount', 0)),
                    'platform': 'etsy',
                    'timestamp': receipt.get('created_timestamp')
                })
        
        return results
    
    def _parse_target_data(self, data: Dict) -> List[Dict]:
        """Parse Target API response"""
        results = []
        
        for item in data.get('products', []):
            results.append({
                'product_id': item.get('tcin'),
                'product_name': item.get('title'),
                'sales': item.get('units_sold', 0),
                'revenue': item.get('revenue', 0),
                'platform': 'target',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return results
