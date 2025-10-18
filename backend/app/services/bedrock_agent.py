"""
backend/app/services/bedrock_agent.py
AWS Bedrock Agent integration for trend analysis
"""

import json
import boto3
from typing import Dict, List, Optional
from datetime import datetime
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class BedrockAgentService:
    """Service for AWS Bedrock Agent interactions"""
    
    def __init__(self):
        self.bedrock_agent = boto3.client(
            'bedrock-agent-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
    async def analyze_trend_data(
        self, 
        product_data: Dict, 
        platform_metrics: List[Dict]
    ) -> Dict:
        """
        Use Bedrock Agent to analyze trend data from multiple sources
        """
        try:
            prompt = self._build_analysis_prompt(product_data, platform_metrics)
            
            response = self.bedrock_runtime.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7
                })
            )
            
            response_body = json.loads(response['body'].read())
            analysis = self._parse_analysis_response(response_body)
            
            logger.info(f"Trend analysis completed for product: {product_data.get('name')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in Bedrock trend analysis: {str(e)}")
            return self._get_fallback_analysis()
    
    async def invoke_agent(
        self,
        session_id: str,
        input_text: str,
        session_state: Optional[Dict] = None
    ) -> Dict:
        """
        Invoke Bedrock Agent for complex queries
        """
        try:
            params = {
                'agentId': settings.BEDROCK_AGENT_ID,
                'agentAliasId': settings.BEDROCK_AGENT_ALIAS_ID,
                'sessionId': session_id,
                'inputText': input_text
            }
            
            if session_state:
                params['sessionState'] = session_state
            
            response = self.bedrock_agent.invoke_agent(**params)
            
            completion = ""
            for event in response.get('completion', []):
                if 'chunk' in event:
                    chunk = event['chunk']
                    completion += chunk.get('bytes', b'').decode('utf-8')
            
            return {
                'response': completion,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error invoking Bedrock Agent: {str(e)}")
            raise
    
    async def predict_trend_trajectory(
        self,
        product_id: str,
        historical_data: List[Dict]
    ) -> Dict:
        """
        Predict product trend trajectory using Bedrock
        """
        try:
            prompt = f"""
            Analyze the following product trend data and predict its trajectory:
            
            Product ID: {product_id}
            Historical Data: {json.dumps(historical_data, indent=2)}
            
            Provide:
            1. Predicted peak date (format: YYYY-MM-DD)
            2. Confidence score (0-1)
            3. Estimated duration in days
            4. Key factors influencing the trend
            5. Recommendation (buy now, wait, avoid)
            
            Format as JSON with these exact keys:
            {{
                "predicted_peak_date": "YYYY-MM-DD or null",
                "confidence_score": 0.0-1.0,
                "duration_days": integer or null,
                "factors": {{"factor_name": importance_score}},
                "recommendation": "string"
            }}
            """
            
            response = self.bedrock_runtime.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5
                })
            )
            
            result = json.loads(response['body'].read())
            prediction = self._parse_prediction(result['content'][0]['text'])
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting trend: {str(e)}")
            return self._get_fallback_prediction()
    
    async def generate_merchant_insights(
        self,
        product_data: Dict,
        competition_data: Dict,
        market_data: Dict
    ) -> Dict:
        """
        Generate AI-powered merchant insights
        """
        try:
            prompt = f"""
            As a business intelligence analyst, analyze this product opportunity:
            
            Product: {product_data.get('name')}
            Category: {product_data.get('category')}
            Current Trend Score: {product_data.get('trend_score')}
            Platforms: {', '.join(product_data.get('platforms', []))}
            
            Competition Level: {competition_data.get('level')}
            Market Size: {market_data.get('size')}
            Growth Rate: {market_data.get('growth_rate')}
            
            Provide merchant-specific insights:
            1. Sourcing recommendations (suppliers, costs, MOQ)
            2. Profit margin estimates
            3. Inventory recommendations (how many units to stock)
            4. Target market segments
            5. Marketing strategy suggestions
            6. Risk factors to consider
            
            Format as JSON.
            """
            
            response = self.bedrock_runtime.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                })
            )
            
            result = json.loads(response['body'].read())
            insights = self._parse_merchant_insights(result['content'][0]['text'])
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating merchant insights: {str(e)}")
            return self._get_fallback_merchant_insights()
    
    async def generate_consumer_insights(
        self,
        product_data: Dict,
        price_history: List[Dict],
        social_proof: Dict
    ) -> Dict:
        """
        Generate AI-powered consumer insights
        """
        try:
            prompt = f"""
            As a shopping advisor, analyze this product for consumers:
            
            Product: {product_data.get('name')}
            Category: {product_data.get('category')}
            Current Price: ${product_data.get('price', 0)}
            Popularity Score: {product_data.get('trend_score')}
            
            Price History: {json.dumps(price_history, indent=2)}
            Social Proof: {json.dumps(social_proof, indent=2)}
            
            Provide consumer-specific insights:
            1. Is this a good time to buy? (yes/no with reasoning)
            2. Price trend analysis (rising/falling/stable)
            3. Value assessment (good value/overpriced/fair)
            4. Alternative recommendations
            5. Best platform to purchase from
            6. Gift suitability (occasions, age groups)
            
            Format as JSON.
            """
            
            response = self.bedrock_runtime.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                })
            )
            
            result = json.loads(response['body'].read())
            insights = self._parse_consumer_insights(result['content'][0]['text'])
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating consumer insights: {str(e)}")
            return self._get_fallback_consumer_insights()
    
    async def analyze_multi_platform_trends(
        self,
        platform_data: Dict[str, List[Dict]]
    ) -> Dict:
        """
        Analyze trends across multiple platforms
        """
        try:
            platform_summary = {}
            for platform, items in platform_data.items():
                platform_summary[platform] = {
                    'item_count': len(items),
                    'total_engagement': sum(
                        item.get('likes', 0) + item.get('shares', 0) + item.get('comments', 0)
                        for item in items
                    ),
                    'avg_views': sum(item.get('views', 0) for item in items) / len(items) if items else 0
                }
            
            prompt = f"""
            Analyze cross-platform trend patterns:
            
            Platform Summary: {json.dumps(platform_summary, indent=2)}
            
            Identify:
            1. Which platforms show strongest trends
            2. Platform-specific patterns (e.g., TikTok viral vs Amazon sales)
            3. Cross-platform correlation insights
            4. Emerging vs declining platforms for this trend
            5. Recommended platform focus for merchants
            
            Format as JSON with actionable insights.
            """
            
            response = self.bedrock_runtime.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.6
                })
            )
            
            result = json.loads(response['body'].read())
            analysis = self._parse_multi_platform_analysis(result['content'][0]['text'])
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing multi-platform trends: {str(e)}")
            return self._get_fallback_platform_analysis()
    
    def _build_analysis_prompt(
        self,
        product_data: Dict,
        platform_metrics: List[Dict]
    ) -> str:
        """Build prompt for trend analysis"""
        return f"""
        Analyze this product's trending status across multiple platforms:
        
        Product: {product_data.get('name')}
        Category: {product_data.get('category')}
        Price: ${product_data.get('price', 0)}
        
        Platform Metrics:
        {json.dumps(platform_metrics, indent=2)}
        
        Calculate and provide:
        1. Overall trend score (0-1, where 1 is highest trending)
        2. Viral velocity (rate of growth, 0-1)
        3. Trend status (emerging/rising/peak/declining/stable)
        4. Platform-specific insights
        5. Competitive analysis
        6. Key factors driving the trend
        
        Provide response as JSON with these exact keys:
        {{
            "trend_score": 0.0-1.0,
            "viral_velocity": 0.0-1.0,
            "status": "emerging|rising|peak|declining|stable",
            "platform_insights": {{"platform_name": "insight"}},
            "competitive_analysis": "string",
            "key_factors": ["factor1", "factor2"],
            "confidence": 0.0-1.0
        }}
        """
    
    def _parse_analysis_response(self, response: Dict) -> Dict:
        """Parse Bedrock analysis response"""
        try:
            content = response.get('content', [{}])[0].get('text', '{}')
            
            # Extract JSON from markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            parsed = json.loads(content)
            
            # Validate required fields
            required_fields = ['trend_score', 'viral_velocity', 'status']
            for field in required_fields:
                if field not in parsed:
                    logger.warning(f"Missing required field: {field}")
                    return self._get_fallback_analysis()
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return self._get_fallback_analysis()
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            return self._get_fallback_analysis()
    
    def _parse_prediction(self, text: str) -> Dict:
        """Parse prediction from text response"""
        try:
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            parsed = json.loads(text)
            
            # Ensure proper types
            return {
                'predicted_peak_date': parsed.get('predicted_peak_date'),
                'confidence_score': float(parsed.get('confidence_score', 0.0)),
                'duration_days': int(parsed.get('duration_days', 0)) if parsed.get('duration_days') else None,
                'recommendation': str(parsed.get('recommendation', 'No recommendation available')),
                'factors': dict(parsed.get('factors', {}))
            }
            
        except Exception as e:
            logger.error(f"Error parsing prediction: {str(e)}")
            return self._get_fallback_prediction()
    
    def _parse_merchant_insights(self, text: str) -> Dict:
        """Parse merchant insights from response"""
        try:
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"Error parsing merchant insights: {str(e)}")
            return self._get_fallback_merchant_insights()
    
    def _parse_consumer_insights(self, text: str) -> Dict:
        """Parse consumer insights from response"""
        try:
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"Error parsing consumer insights: {str(e)}")
            return self._get_fallback_consumer_insights()
    
    def _parse_multi_platform_analysis(self, text: str) -> Dict:
        """Parse multi-platform analysis from response"""
        try:
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"Error parsing platform analysis: {str(e)}")
            return self._get_fallback_platform_analysis()
    
    def _get_fallback_analysis(self) -> Dict:
        """Fallback analysis when Bedrock fails"""
        return {
            'trend_score': 0.5,
            'viral_velocity': 0.0,
            'status': 'stable',
            'platform_insights': {},
            'competitive_analysis': 'Analysis service temporarily unavailable',
            'key_factors': ['Service unavailable'],
            'confidence': 0.3
        }
    
    def _get_fallback_prediction(self) -> Dict:
        """Fallback prediction"""
        return {
            'predicted_peak_date': None,
            'confidence_score': 0.0,
            'duration_days': None,
            'recommendation': 'Insufficient data for prediction',
            'factors': {}
        }
    
    def _get_fallback_merchant_insights(self) -> Dict:
        """Fallback merchant insights"""
        return {
            'sourcing_recommendations': [
                {
                    'supplier': 'General Wholesaler',
                    'estimated_cost': 0.0,
                    'notes': 'AI analysis unavailable'
                }
            ],
            'profit_margin_estimate': 0.0,
            'inventory_recommendation': {
                'recommended_units': 0,
                'reasoning': 'AI analysis unavailable'
            },
            'target_segments': [],
            'marketing_suggestions': [],
            'risk_factors': ['AI service unavailable - manual analysis recommended']
        }
    
    def _get_fallback_consumer_insights(self) -> Dict:
        """Fallback consumer insights"""
        return {
            'good_time_to_buy': False,
            'reasoning': 'AI analysis unavailable',
            'price_trend': 'unknown',
            'value_assessment': 'unknown',
            'alternatives': [],
            'best_platform': 'unknown',
            'gift_suitability': {
                'occasions': [],
                'age_groups': []
            }
        }
    
    def _get_fallback_platform_analysis(self) -> Dict:
        """Fallback platform analysis"""
        return {
            'strongest_platforms': [],
            'platform_patterns': {},
            'cross_platform_insights': 'AI analysis unavailable',
            'emerging_platforms': [],
            'declining_platforms': [],
            'recommended_focus': 'AI analysis unavailable'
        }
