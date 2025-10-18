"""
backend/app/services/amazon_q_service.py
Amazon Q integration for policy and metadata queries
"""

import boto3
import json
from typing import Dict, List, Optional
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AmazonQService:
    """Service for Amazon Q business intelligence queries"""
    
    def __init__(self):
        self.q_client = boto3.client(
            'qbusiness',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.app_id = settings.AMAZON_Q_APP_ID
        self.user_id = settings.AMAZON_Q_USER_ID
    
    async def query_product_policy(
        self,
        product_category: str,
        platform: str
    ) -> Dict:
        """Query product listing policies and restrictions"""
        try:
            query = f"What are the listing policies and restrictions for {product_category} products on {platform}?"
            
            response = self.q_client.chat_sync(
                applicationId=self.app_id,
                userId=self.user_id,
                userMessage=query
            )
            
            return {
                'category': product_category,
                'platform': platform,
                'policies': self._parse_policy_response(response),
                'restrictions': self._extract_restrictions(response),
                'compliance_notes': self._extract_compliance(response)
            }
        
        except Exception as e:
            logger.error(f"Amazon Q policy query error: {str(e)}")
            return {'error': str(e)}
    
    async def query_product_metadata(
        self,
        product_id: str
    ) -> Dict:
        """Query detailed product metadata"""
        try:
            query = f"Provide detailed metadata and attributes for product ID: {product_id}"
            
            response = self.q_client.chat_sync(
                applicationId=self.app_id,
                userId=self.user_id,
                userMessage=query
            )
            
            return self._parse_metadata_response(response)
        
        except Exception as e:
            logger.error(f"Amazon Q metadata query error: {str(e)}")
            return {}
    
    async def query_category_insights(
        self,
        category: str
    ) -> Dict:
        """Get insights about product category"""
        try:
            query = f"Provide market insights, trends, and key metrics for {category} category"
            
            response = self.q_client.chat_sync(
                applicationId=self.app_id,
                userId=self.user_id,
                userMessage=query
            )
            
            return {
                'category': category,
                'insights': self._parse_insights(response),
                'key_metrics': self._extract_metrics(response),
                'recommendations': self._extract_recommendations(response)
            }
        
        except Exception as e:
            logger.error(f"Amazon Q category insights error: {str(e)}")
            return {}
    
    async def query_compliance_check(
        self,
        product_data: Dict
    ) -> Dict:
        """Check product compliance across platforms"""
        try:
            query = f"""
            Check compliance for this product:
            Name: {product_data.get('name')}
            Category: {product_data.get('category')}
            Description: {product_data.get('description')}
            
            Verify compliance for Amazon, eBay, Walmart, Etsy, and Target.
            """
            
            response = self.q_client.chat_sync(
                applicationId=self.app_id,
                userId=self.user_id,
                userMessage=query
            )
            
            return {
                'product_id': product_data.get('id'),
                'compliant': self._check_compliance(response),
                'platform_status': self._parse_platform_compliance(response),
                'issues': self._extract_compliance_issues(response),
                'recommendations': self._extract_recommendations(response)
            }
        
        except Exception as e:
            logger.error(f"Amazon Q compliance check error: {str(e)}")
            return {'error': str(e)}
    
    def _parse_policy_response(self, response: Dict) -> List[str]:
        """Parse policy information from Q response"""
        system_message = response.get('systemMessage', '')
        
        # Extract policy points
        policies = []
        lines = system_message.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['policy', 'requirement', 'must', 'required']):
                policies.append(line.strip())
        
        return policies
    
    def _extract_restrictions(self, response: Dict) -> List[str]:
        """Extract restrictions from response"""
        system_message = response.get('systemMessage', '')
        
        restrictions = []
        lines = system_message.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['restrict', 'prohibit', 'not allow', 'forbidden']):
                restrictions.append(line.strip())
        
        return restrictions
    
    def _extract_compliance(self, response: Dict) -> List[str]:
        """Extract compliance notes"""
        system_message = response.get('systemMessage', '')
        
        compliance = []
        lines = system_message.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['comply', 'compliance', 'regulation', 'standard']):
                compliance.append(line.strip())
        
        return compliance
    
    def _parse_metadata_response(self, response: Dict) -> Dict:
        """Parse metadata from response"""
        system_message = response.get('systemMessage', '')
        
        # Basic parsing - in production, use more sophisticated NLP
        metadata = {
            'description': system_message,
            'attributes': {},
            'specifications': []
        }
        
        return metadata
    
    def _parse_insights(self, response: Dict) -> List[str]:
        """Parse insights from response"""
        system_message = response.get('systemMessage', '')
        
        insights = []
        lines = system_message.split('\n')
        
        for line in lines:
            if line.strip() and len(line.strip()) > 20:
                insights.append(line.strip())
        
        return insights
    
    def _extract_metrics(self, response: Dict) -> Dict:
        """Extract metrics from response"""
        # Placeholder - implement metric extraction logic
        return {
            'market_size': 'Unknown',
            'growth_rate': 'Unknown',
            'competition_level': 'Unknown'
        }
    
    def _extract_recommendations(self, response: Dict) -> List[str]:
        """Extract recommendations from response"""
        system_message = response.get('systemMessage', '')
        
        recommendations = []
        lines = system_message.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider']):
                recommendations.append(line.strip())
        
        return recommendations
    
    def _check_compliance(self, response: Dict) -> bool:
        """Check if product is compliant"""
        system_message = response.get('systemMessage', '').lower()
        
        # Check for non-compliance indicators
        non_compliant_keywords = ['not compliant', 'violates', 'prohibited', 'restricted']
        
        for keyword in non_compliant_keywords:
            if keyword in system_message:
                return False
        
        return True
    
    def _parse_platform_compliance(self, response: Dict) -> Dict[str, bool]:
        """Parse compliance status per platform"""
        system_message = response.get('systemMessage', '').lower()
        
        platforms = ['amazon', 'ebay', 'walmart', 'etsy', 'target']
        status = {}
        
        for platform in platforms:
            if platform in system_message:
                # Check for compliance indicators
                compliant = 'compliant' in system_message or 'allowed' in system_message
                status[platform] = compliant
            else:
                status[platform] = True  # Default to compliant if not mentioned
        
        return status
    
    def _extract_compliance_issues(self, response: Dict) -> List[str]:
        """Extract compliance issues"""
        system_message = response.get('systemMessage', '')
        
        issues = []
        lines = system_message.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['issue', 'problem', 'violation', 'concern']):
                issues.append(line.strip())
        
        return issues
