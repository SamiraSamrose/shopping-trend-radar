"""
backend/app/services/nova_connector.py
Nova SDK integration for social media APIs
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.config import get_settings, SUPPORTED_PLATFORMS
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class NovaConnector:
    """Service for connecting to multiple social media platforms via Nova SDK"""
    
    def __init__(self):
        self.api_key = settings.NOVA_API_KEY
        self.base_url = settings.NOVA_API_URL
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_youtube_trends(
        self,
        keywords: List[str],
        max_results: int = 50
    ) -> List[Dict]:
        """Fetch trending products from YouTube"""
        try:
            results = []
            
            for keyword in keywords:
                params = {
                    'part': 'snippet,statistics',
                    'q': keyword,
                    'type': 'video',
                    'order': 'viewCount',
                    'publishedAfter': (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z',
                    'maxResults': max_results,
                    'key': settings.YOUTUBE_API_KEY
                }
                
                async with self.session.get(
                    'https://www.googleapis.com/youtube/v3/search',
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = self._parse_youtube_response(data, keyword)
                        results.extend(videos)
            
            logger.info(f"Fetched {len(results)} YouTube trends")
            return results
            
        except Exception as e:
            logger.error(f"YouTube fetch error: {str(e)}")
            return []
    
    async def fetch_tiktok_trends(
        self,
        hashtags: List[str],
        max_results: int = 50
    ) -> List[Dict]:
        """Fetch trending products from TikTok"""
        try:
            results = []
            
            headers = {
                'Authorization': f'Bearer {settings.TIKTOK_CLIENT_KEY}',
                'Content-Type': 'application/json'
            }
            
            for hashtag in hashtags:
                payload = {
                    'query': {
                        'hashtag': hashtag,
                        'max_count': max_results
                    }
                }
                
                async with self.session.post(
                    'https://open-api.tiktok.com/research/query/',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = self._parse_tiktok_response(data, hashtag)
                        results.extend(videos)
            
            logger.info(f"Fetched {len(results)} TikTok trends")
            return results
            
        except Exception as e:
            logger.error(f"TikTok fetch error: {str(e)}")
            return []
    
    async def fetch_instagram_trends(
        self,
        hashtags: List[str]
    ) -> List[Dict]:
        """Fetch trending products from Instagram"""
        try:
            results = []
            
            for hashtag in hashtags:
                params = {
                    'q': hashtag,
                    'type': 'hashtag',
                    'access_token': settings.INSTAGRAM_ACCESS_TOKEN
                }
                
                async with self.session.get(
                    f'https://graph.instagram.com/ig_hashtag_search',
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Get top posts for this hashtag
                        if data.get('data'):
                            hashtag_id = data['data'][0]['id']
                            posts = await self._fetch_instagram_hashtag_posts(hashtag_id)
                            results.extend(posts)
            
            logger.info(f"Fetched {len(results)} Instagram trends")
            return results
            
        except Exception as e:
            logger.error(f"Instagram fetch error: {str(e)}")
            return []
    
    async def _fetch_instagram_hashtag_posts(
        self,
        hashtag_id: str
    ) -> List[Dict]:
        """Fetch recent posts for an Instagram hashtag"""
        try:
            params = {
                'user_id': settings.INSTAGRAM_ACCESS_TOKEN.split('.')[0],
                'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
                'access_token': settings.INSTAGRAM_ACCESS_TOKEN
            }
            
            async with self.session.get(
                f'https://graph.instagram.com/{hashtag_id}/recent_media',
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_instagram_response(data)
                return []
                
        except Exception as e:
            logger.error(f"Instagram posts fetch error: {str(e)}")
            return []
    
    async def fetch_pinterest_trends(
        self,
        keywords: List[str]
    ) -> List[Dict]:
        """Fetch trending products from Pinterest"""
        try:
            results = []
            
            headers = {
                'Authorization': f'Bearer {settings.PINTEREST_ACCESS_TOKEN}'
            }
            
            for keyword in keywords:
                params = {
                    'query': keyword,
                    'limit': 50
                }
                
                async with self.session.get(
                    'https://api.pinterest.com/v5/search/pins',
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        pins = self._parse_pinterest_response(data, keyword)
                        results.extend(pins)
            
            logger.info(f"Fetched {len(results)} Pinterest trends")
            return results
            
        except Exception as e:
            logger.error(f"Pinterest fetch error: {str(e)}")
            return []
    
    async def fetch_meta_trends(
        self,
        keywords: List[str]
    ) -> List[Dict]:
        """Fetch trending products from Meta/Facebook"""
        try:
            results = []
            
            params = {
                'access_token': f'{settings.META_APP_ID}|{settings.META_APP_SECRET}',
                'q': ','.join(keywords),
                'type': 'post',
                'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares'
            }
            
            async with self.session.get(
                'https://graph.facebook.com/v18.0/search',
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = self._parse_meta_response(data)
                    results.extend(posts)
            
            logger.info(f"Fetched {len(results)} Meta trends")
            return results
            
        except Exception as e:
            logger.error(f"Meta fetch error: {str(e)}")
            return []
    
    async def fetch_all_platforms(
        self,
        keywords: List[str],
        hashtags: List[str]
    ) -> Dict[str, List[Dict]]:
        """Fetch trends from all platforms concurrently"""
        tasks = [
            self.fetch_youtube_trends(keywords),
            self.fetch_tiktok_trends(hashtags),
            self.fetch_instagram_trends(hashtags),
            self.fetch_pinterest_trends(keywords),
            self.fetch_meta_trends(keywords)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'youtube': results[0] if not isinstance(results[0], Exception) else [],
            'tiktok': results[1] if not isinstance(results[1], Exception) else [],
            'instagram': results[2] if not isinstance(results[2], Exception) else [],
            'pinterest': results[3] if not isinstance(results[3], Exception) else [],
            'meta': results[4] if not isinstance(results[4], Exception) else []
        }
    
    def _parse_youtube_response(self, data: Dict, keyword: str) -> List[Dict]:
        """Parse YouTube API response"""
        results = []
        
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId')
            
            if video_id:
                results.append({
                    'platform': 'youtube',
                    'id': video_id,
                    'title': snippet.get('title'),
                    'description': snippet.get('description'),
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                    'published_at': snippet.get('publishedAt'),
                    'channel': snippet.get('channelTitle'),
                    'keyword': keyword,
                    'fetched_at': datetime.utcnow().isoformat()
                })
        
        return results
    
    def _parse_tiktok_response(self, data: Dict, hashtag: str) -> List[Dict]:
        """Parse TikTok API response"""
        results = []
        
        for video in data.get('data', {}).get('videos', []):
            results.append({
                'platform': 'tiktok',
                'id': video.get('id'),
                'description': video.get('video_description'),
                'views': video.get('view_count', 0),
                'likes': video.get('like_count', 0),
                'shares': video.get('share_count', 0),
                'comments': video.get('comment_count', 0),
                'hashtag': hashtag,
                'created_at': video.get('create_time'),
                'fetched_at': datetime.utcnow().isoformat()
            })
        
        return results
    
    def _parse_instagram_response(self, data: Dict) -> List[Dict]:
        """Parse Instagram API response"""
        results = []
        
        for post in data.get('data', []):
            results.append({
                'platform': 'instagram',
                'id': post.get('id'),
                'caption': post.get('caption'),
                'media_url': post.get('media_url'),
                'likes': post.get('like_count', 0),
                'comments': post.get('comments_count', 0),
                'timestamp': post.get('timestamp'),
                'fetched_at': datetime.utcnow().isoformat()
            })
        
        return results
    
    def _parse_pinterest_response(self, data: Dict, keyword: str) -> List[Dict]:
        """Parse Pinterest API response"""
        results = []
        
        for pin in data.get('items', []):
            results.append({
                'platform': 'pinterest',
                'id': pin.get('id'),
                'title': pin.get('title'),
                'description': pin.get('description'),
                'image_url': pin.get('media', {}).get('images', {}).get('original', {}).get('url'),
                'url': pin.get('link'),
                'saves': pin.get('save_count', 0),
                'keyword': keyword,
                'fetched_at': datetime.utcnow().isoformat()
            })
        
        return results
    
    def _parse_meta_response(self, data: Dict) -> List[Dict]:
        """Parse Meta/Facebook API response"""
        results = []
        
        for post in data.get('data', []):
            likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
            comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
            shares = post.get('shares', {}).get('count', 0)
            
            results.append({
                'platform': 'meta',
                'id': post.get('id'),
                'message': post.get('message'),
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'engagement': likes + comments + shares,
                'created_at': post.get('created_time'),
                'fetched_at': datetime.utcnow().isoformat()
            })
        
        return results
