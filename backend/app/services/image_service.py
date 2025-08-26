"""
Image Service
Integrates with Unsplash and Pexels for dynamic image fetching
"""

import os
import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import random

logger = logging.getLogger(__name__)

class ImageProvider:
    """Base class for image providers"""
    
    async def search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError
    
    async def get_image(self, image_id: str) -> Dict[str, Any]:
        raise NotImplementedError

class UnsplashProvider(ImageProvider):
    """Unsplash API integration"""
    
    def __init__(self, access_key: str):
        self.access_key = access_key
        self.base_url = "https://api.unsplash.com"
        self.headers = {
            "Authorization": f"Client-ID {access_key}"
        }
    
    async def search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Search for images on Unsplash"""
        
        url = f"{self.base_url}/search/photos"
        params = {
            "query": query,
            "per_page": count,
            "orientation": "landscape",
            "content_filter": "high"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_results(data.get("results", []))
                    else:
                        logger.error(f"Unsplash API error: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Error fetching from Unsplash: {str(e)}")
                return []
    
    def _format_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Format Unsplash results to standard format"""
        
        formatted = []
        for item in results:
            formatted.append({
                "id": item.get("id"),
                "provider": "unsplash",
                "url": item.get("urls", {}).get("regular"),
                "thumbnail": item.get("urls", {}).get("small"),
                "full": item.get("urls", {}).get("full"),
                "width": item.get("width"),
                "height": item.get("height"),
                "description": item.get("description") or item.get("alt_description", ""),
                "author": item.get("user", {}).get("name", "Unknown"),
                "author_url": item.get("user", {}).get("links", {}).get("html", ""),
                "download_url": item.get("links", {}).get("download"),
                "attribution_required": True,
                "license": "Unsplash License"
            })
        return formatted

class PexelsProvider(ImageProvider):
    """Pexels API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {
            "Authorization": api_key
        }
    
    async def search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Search for images on Pexels"""
        
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "per_page": count,
            "orientation": "landscape"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_results(data.get("photos", []))
                    else:
                        logger.error(f"Pexels API error: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Error fetching from Pexels: {str(e)}")
                return []
    
    def _format_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Format Pexels results to standard format"""
        
        formatted = []
        for item in results:
            formatted.append({
                "id": str(item.get("id")),
                "provider": "pexels",
                "url": item.get("src", {}).get("large"),
                "thumbnail": item.get("src", {}).get("medium"),
                "full": item.get("src", {}).get("original"),
                "width": item.get("width"),
                "height": item.get("height"),
                "description": item.get("alt", ""),
                "author": item.get("photographer", "Unknown"),
                "author_url": item.get("photographer_url", ""),
                "download_url": item.get("src", {}).get("original"),
                "attribution_required": True,
                "license": "Pexels License"
            })
        return formatted

class ImageService:
    """
    Main service for managing image search and caching
    """
    
    def __init__(self):
        self.cache_dir = Path("cache/images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(days=7)
        
        # Initialize providers (keys should be in environment variables)
        self.providers = []
        
        unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if unsplash_key:
            self.providers.append(UnsplashProvider(unsplash_key))
            logger.info("✅ Unsplash provider initialized")
        
        pexels_key = os.getenv("PEXELS_API_KEY")
        if pexels_key:
            self.providers.append(PexelsProvider(pexels_key))
            logger.info("✅ Pexels provider initialized")
        
        if not self.providers:
            logger.warning("⚠️ No image providers configured. Using fallback images.")
            
        # Industry-specific search terms
        self.industry_keywords = {
            "restaurant": [
                "restaurant interior", "food presentation", "chef cooking",
                "dining table", "restaurant kitchen", "wine selection",
                "restaurant ambiance", "food service", "restaurant bar"
            ],
            "healthcare": [
                "medical clinic", "hospital", "doctor patient", "medical equipment",
                "healthcare professional", "medical consultation", "pharmacy",
                "health wellness", "medical office"
            ],
            "ecommerce": [
                "online shopping", "ecommerce", "product photography",
                "shopping cart", "delivery package", "warehouse logistics",
                "retail store", "customer service", "product display"
            ],
            "services": [
                "business meeting", "professional service", "office work",
                "consulting", "customer support", "business handshake",
                "corporate office", "team collaboration", "business presentation"
            ],
            "education": [
                "classroom", "students learning", "teacher teaching",
                "library study", "graduation", "online education",
                "school campus", "education technology", "student success"
            ]
        }
        
        # Fallback images for when APIs are not available
        self.fallback_images = {
            "restaurant": [
                {
                    "id": "fallback_rest_1",
                    "provider": "fallback",
                    "url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
                    "thumbnail": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400",
                    "description": "Restaurant interior",
                    "author": "Unsplash",
                    "attribution_required": False
                }
            ],
            "healthcare": [
                {
                    "id": "fallback_health_1",
                    "provider": "fallback",
                    "url": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d",
                    "thumbnail": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=400",
                    "description": "Medical consultation",
                    "author": "Unsplash",
                    "attribution_required": False
                }
            ],
            "ecommerce": [
                {
                    "id": "fallback_ecom_1",
                    "provider": "fallback",
                    "url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d",
                    "thumbnail": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400",
                    "description": "Online shopping",
                    "author": "Unsplash",
                    "attribution_required": False
                }
            ],
            "services": [
                {
                    "id": "fallback_serv_1",
                    "provider": "fallback",
                    "url": "https://images.unsplash.com/photo-1556761175-4b46a572b786",
                    "thumbnail": "https://images.unsplash.com/photo-1556761175-4b46a572b786?w=400",
                    "description": "Business meeting",
                    "author": "Unsplash",
                    "attribution_required": False
                }
            ],
            "education": [
                {
                    "id": "fallback_edu_1",
                    "provider": "fallback",
                    "url": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1",
                    "thumbnail": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=400",
                    "description": "University campus",
                    "author": "Unsplash",
                    "attribution_required": False
                }
            ]
        }
    
    async def search_images(
        self,
        query: str,
        count: int = 5,
        industry: Optional[str] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for images across all configured providers
        
        Args:
            query: Search query
            count: Number of images to return
            industry: Industry type for better results
            use_cache: Whether to use cached results
            
        Returns:
            List of image dictionaries
        """
        
        # Check cache first
        if use_cache:
            cached = self._get_cached_results(query)
            if cached:
                logger.info(f"🎯 Using cached images for query: {query}")
                return cached[:count]
        
        # If no providers configured, use fallback
        if not self.providers:
            return self._get_fallback_images(industry or "services", count)
        
        # Search across all providers
        all_results = []
        for provider in self.providers:
            try:
                results = await provider.search(query, count)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Error searching with {provider.__class__.__name__}: {str(e)}")
        
        # If no results, try industry-specific search
        if not all_results and industry:
            industry_query = self._get_industry_query(industry)
            for provider in self.providers:
                try:
                    results = await provider.search(industry_query, count)
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Error with industry search: {str(e)}")
        
        # If still no results, use fallback
        if not all_results:
            return self._get_fallback_images(industry or "services", count)
        
        # Cache results
        if use_cache and all_results:
            self._cache_results(query, all_results)
        
        # Return requested count
        return all_results[:count]
    
    async def get_images_for_template(
        self,
        template_id: str,
        industry: str,
        sections: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get images for all sections of a template
        
        Args:
            template_id: Template identifier
            industry: Industry type
            sections: List of section names needing images
            
        Returns:
            Dictionary mapping section names to image lists
        """
        
        section_images = {}
        
        # Define section-specific queries
        section_queries = {
            "hero": f"{industry} hero banner professional",
            "about": f"{industry} about us team",
            "services": f"{industry} services offering",
            "gallery": f"{industry} portfolio gallery",
            "testimonials": f"happy customers {industry}",
            "contact": f"{industry} contact location",
            "products": f"{industry} products showcase",
            "team": f"{industry} team professionals",
            "features": f"{industry} features benefits"
        }
        
        for section in sections:
            # Get appropriate query for section
            if section in section_queries:
                query = section_queries[section]
            else:
                query = f"{industry} {section}"
            
            # Search for images
            images = await self.search_images(
                query=query,
                count=3,
                industry=industry
            )
            
            section_images[section] = images
        
        return section_images
    
    async def download_image(self, image_url: str, save_path: Path) -> bool:
        """
        Download an image to local storage
        
        Args:
            image_url: URL of the image to download
            save_path: Path where to save the image
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        save_path.parent.mkdir(parents=True, exist_ok=True)
                        save_path.write_bytes(content)
                        logger.info(f"✅ Image downloaded: {save_path}")
                        return True
                    else:
                        logger.error(f"Failed to download image: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return False
    
    def get_attribution_html(self, image: Dict[str, Any]) -> str:
        """
        Generate attribution HTML for an image
        
        Args:
            image: Image dictionary
            
        Returns:
            HTML string for attribution
        """
        
        if not image.get("attribution_required"):
            return ""
        
        provider = image.get("provider", "Unknown")
        author = image.get("author", "Unknown")
        author_url = image.get("author_url", "#")
        
        if provider == "unsplash":
            return f'Foto por <a href="{author_url}" target="_blank">{author}</a> no <a href="https://unsplash.com" target="_blank">Unsplash</a>'
        elif provider == "pexels":
            return f'Foto por <a href="{author_url}" target="_blank">{author}</a> no <a href="https://pexels.com" target="_blank">Pexels</a>'
        else:
            return f'Foto por {author}'
    
    def _get_industry_query(self, industry: str) -> str:
        """Get a random industry-specific search query"""
        
        if industry in self.industry_keywords:
            keywords = self.industry_keywords[industry]
            return random.choice(keywords)
        return f"{industry} business professional"
    
    def _get_fallback_images(self, industry: str, count: int) -> List[Dict[str, Any]]:
        """Get fallback images when APIs are not available"""
        
        if industry in self.fallback_images:
            images = self.fallback_images[industry]
        else:
            # Use services as default fallback
            images = self.fallback_images.get("services", [])
        
        # Duplicate images if we need more than available
        result = []
        while len(result) < count:
            result.extend(images)
        
        return result[:count]
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for a query"""
        
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_cached_results(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached results for a query"""
        
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            # Check if cache is still valid
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - file_time < self.cache_duration:
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error reading cache: {str(e)}")
        
        return None
    
    def _cache_results(self, query: str, results: List[Dict[str, Any]]):
        """Cache search results"""
        
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing cache: {str(e)}")
    
    async def optimize_images_for_web(
        self,
        images: List[Dict[str, Any]],
        target_width: int = 1920,
        quality: int = 85
    ) -> List[Dict[str, Any]]:
        """
        Optimize images for web usage
        
        Args:
            images: List of image dictionaries
            target_width: Maximum width for images
            quality: JPEG quality (1-100)
            
        Returns:
            List of optimized image dictionaries
        """
        
        optimized = []
        
        for image in images:
            # For now, just return the medium/regular sized URLs
            # In production, you would actually process the images
            optimized_image = image.copy()
            
            # Use smaller versions when available
            if image.get("provider") == "unsplash":
                # Unsplash allows size parameters in URL
                base_url = image.get("url", "")
                if base_url:
                    optimized_image["url"] = f"{base_url}&w={target_width}&q={quality}"
            
            optimized.append(optimized_image)
        
        return optimized

# Create singleton instance
image_service = ImageService()