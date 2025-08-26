"""
CDN Integration Service for KenzySites
"""

import boto3
import hashlib
import mimetypes
import os
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta
import aiohttp
import asyncio
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class CDNProvider:
    """Base CDN provider interface"""
    
    async def upload(self, file_path: str, content: bytes, content_type: str) -> str:
        """Upload file to CDN"""
        raise NotImplementedError
    
    async def delete(self, file_path: str) -> bool:
        """Delete file from CDN"""
        raise NotImplementedError
    
    async def purge(self, paths: List[str]) -> bool:
        """Purge cache for specific paths"""
        raise NotImplementedError
    
    def get_url(self, file_path: str) -> str:
        """Get CDN URL for file"""
        raise NotImplementedError

class CloudFrontProvider(CDNProvider):
    """AWS CloudFront CDN provider"""
    
    def __init__(
        self,
        distribution_id: str,
        bucket_name: str,
        aws_access_key: str,
        aws_secret_key: str,
        region: str = "us-east-1",
        domain: str = None
    ):
        self.distribution_id = distribution_id
        self.bucket_name = bucket_name
        self.domain = domain or f"https://{distribution_id}.cloudfront.net"
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        self.cloudfront_client = boto3.client(
            'cloudfront',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
    
    async def upload(self, file_path: str, content: bytes, content_type: str) -> str:
        """Upload file to S3 and CloudFront"""
        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=content,
                ContentType=content_type,
                CacheControl='public, max-age=31536000',
                ACL='public-read'
            )
            
            return self.get_url(file_path)
        except Exception as e:
            logger.error(f"Error uploading to CloudFront: {e}")
            raise
    
    async def delete(self, file_path: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            
            # Invalidate CloudFront cache
            await self.purge([file_path])
            
            return True
        except Exception as e:
            logger.error(f"Error deleting from CloudFront: {e}")
            return False
    
    async def purge(self, paths: List[str]) -> bool:
        """Invalidate CloudFront cache"""
        try:
            # Add leading slash if not present
            paths = [f"/{p}" if not p.startswith('/') else p for p in paths]
            
            response = self.cloudfront_client.create_invalidation(
                DistributionId=self.distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': str(datetime.now().timestamp())
                }
            )
            
            return response['Invalidation']['Status'] == 'InProgress'
        except Exception as e:
            logger.error(f"Error purging CloudFront cache: {e}")
            return False
    
    def get_url(self, file_path: str) -> str:
        """Get CloudFront URL for file"""
        return urljoin(self.domain, file_path)

class CloudflareProvider(CDNProvider):
    """Cloudflare CDN provider"""
    
    def __init__(
        self,
        account_id: str,
        api_token: str,
        zone_id: str,
        domain: str
    ):
        self.account_id = account_id
        self.api_token = api_token
        self.zone_id = zone_id
        self.domain = domain
        self.api_base = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    async def upload(self, file_path: str, content: bytes, content_type: str) -> str:
        """Upload file to Cloudflare R2"""
        # Cloudflare R2 implementation
        # This would use Cloudflare R2 API for object storage
        async with aiohttp.ClientSession() as session:
            # Upload to R2
            url = f"{self.api_base}/accounts/{self.account_id}/r2/buckets/kenzysites/objects/{file_path}"
            
            async with session.put(
                url,
                headers={**self.headers, "Content-Type": content_type},
                data=content
            ) as response:
                if response.status == 200:
                    return self.get_url(file_path)
                else:
                    raise Exception(f"Failed to upload to Cloudflare: {await response.text()}")
    
    async def delete(self, file_path: str) -> bool:
        """Delete file from Cloudflare R2"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.api_base}/accounts/{self.account_id}/r2/buckets/kenzysites/objects/{file_path}"
            
            async with session.delete(url, headers=self.headers) as response:
                return response.status == 200
    
    async def purge(self, paths: List[str]) -> bool:
        """Purge Cloudflare cache"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.api_base}/zones/{self.zone_id}/purge_cache"
            
            # Convert paths to full URLs
            urls = [urljoin(self.domain, path) for path in paths]
            
            data = {"files": urls}
            
            async with session.post(url, headers=self.headers, json=data) as response:
                return response.status == 200
    
    def get_url(self, file_path: str) -> str:
        """Get Cloudflare CDN URL"""
        return urljoin(self.domain, file_path)

class BunnyCDNProvider(CDNProvider):
    """BunnyCDN provider"""
    
    def __init__(
        self,
        storage_zone: str,
        storage_key: str,
        pull_zone: str,
        api_key: str
    ):
        self.storage_zone = storage_zone
        self.storage_key = storage_key
        self.pull_zone = pull_zone
        self.api_key = api_key
        self.storage_api = f"https://storage.bunnycdn.com/{storage_zone}"
        self.api_base = "https://api.bunny.net"
    
    async def upload(self, file_path: str, content: bytes, content_type: str) -> str:
        """Upload file to BunnyCDN storage"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.storage_api}/{file_path}"
            headers = {
                "AccessKey": self.storage_key,
                "Content-Type": content_type
            }
            
            async with session.put(url, headers=headers, data=content) as response:
                if response.status in [200, 201]:
                    return self.get_url(file_path)
                else:
                    raise Exception(f"Failed to upload to BunnyCDN: {await response.text()}")
    
    async def delete(self, file_path: str) -> bool:
        """Delete file from BunnyCDN storage"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.storage_api}/{file_path}"
            headers = {"AccessKey": self.storage_key}
            
            async with session.delete(url, headers=headers) as response:
                return response.status == 200
    
    async def purge(self, paths: List[str]) -> bool:
        """Purge BunnyCDN cache"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.api_base}/purge"
            headers = {"AccessKey": self.api_key}
            
            # BunnyCDN expects full URLs
            urls = [urljoin(f"https://{self.pull_zone}.b-cdn.net", path) for path in paths]
            
            for url_to_purge in urls:
                async with session.post(
                    url,
                    headers=headers,
                    params={"url": url_to_purge}
                ) as response:
                    if response.status != 200:
                        return False
            
            return True
    
    def get_url(self, file_path: str) -> str:
        """Get BunnyCDN URL"""
        return f"https://{self.pull_zone}.b-cdn.net/{file_path}"

class CDNService:
    """Main CDN service for managing multiple providers"""
    
    def __init__(self, provider: CDNProvider = None):
        self.provider = provider
        self.local_cache_dir = Path("/tmp/cdn_cache")
        self.local_cache_dir.mkdir(exist_ok=True)
        self.optimization_enabled = True
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
        self.supported_asset_formats = {'.css', '.js', '.json', '.xml', '.txt', '.pdf'}
    
    def set_provider(self, provider: CDNProvider):
        """Set CDN provider"""
        self.provider = provider
    
    async def upload_file(
        self,
        file_path: str,
        content: bytes,
        content_type: str = None,
        optimize: bool = True
    ) -> str:
        """Upload file to CDN with optimization"""
        if not self.provider:
            raise ValueError("No CDN provider configured")
        
        # Detect content type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or 'application/octet-stream'
        
        # Optimize content if enabled
        if optimize and self.optimization_enabled:
            content = await self._optimize_content(file_path, content, content_type)
        
        # Generate versioned filename
        file_hash = hashlib.md5(content).hexdigest()[:8]
        versioned_path = self._add_version_to_path(file_path, file_hash)
        
        # Upload to CDN
        cdn_url = await self.provider.upload(versioned_path, content, content_type)
        
        # Cache locally for faster access
        await self._cache_locally(versioned_path, content)
        
        return cdn_url
    
    async def upload_directory(
        self,
        local_dir: str,
        cdn_prefix: str = "",
        optimize: bool = True
    ) -> Dict[str, str]:
        """Upload entire directory to CDN"""
        uploaded_files = {}
        local_path = Path(local_dir)
        
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                cdn_path = os.path.join(cdn_prefix, str(relative_path))
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                cdn_url = await self.upload_file(cdn_path, content, optimize=optimize)
                uploaded_files[str(relative_path)] = cdn_url
        
        return uploaded_files
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from CDN"""
        if not self.provider:
            raise ValueError("No CDN provider configured")
        
        success = await self.provider.delete(file_path)
        
        # Remove from local cache
        if success:
            await self._remove_from_local_cache(file_path)
        
        return success
    
    async def purge_cache(self, paths: List[str]) -> bool:
        """Purge CDN cache for specific paths"""
        if not self.provider:
            raise ValueError("No CDN provider configured")
        
        return await self.provider.purge(paths)
    
    async def purge_all(self) -> bool:
        """Purge entire CDN cache"""
        return await self.purge_cache(["/*"])
    
    def get_url(self, file_path: str) -> str:
        """Get CDN URL for file"""
        if not self.provider:
            raise ValueError("No CDN provider configured")
        
        return self.provider.get_url(file_path)
    
    async def _optimize_content(
        self,
        file_path: str,
        content: bytes,
        content_type: str
    ) -> bytes:
        """Optimize content before uploading"""
        file_ext = Path(file_path).suffix.lower()
        
        # Optimize images
        if file_ext in self.supported_image_formats:
            content = await self._optimize_image(content, file_ext)
        
        # Optimize CSS
        elif file_ext == '.css':
            content = self._minify_css(content)
        
        # Optimize JavaScript
        elif file_ext == '.js':
            content = self._minify_js(content)
        
        # Optimize JSON
        elif file_ext == '.json':
            content = self._minify_json(content)
        
        return content
    
    async def _optimize_image(self, content: bytes, format: str) -> bytes:
        """Optimize image content"""
        # In a real implementation, use PIL/Pillow for image optimization
        # For now, return original content
        return content
    
    def _minify_css(self, content: bytes) -> bytes:
        """Minify CSS content"""
        css_text = content.decode('utf-8')
        
        # Simple CSS minification (in production, use a proper CSS minifier)
        import re
        
        # Remove comments
        css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_text = re.sub(r'\s+', ' ', css_text)
        css_text = re.sub(r'\s*([{}:;,])\s*', r'\1', css_text)
        
        return css_text.encode('utf-8')
    
    def _minify_js(self, content: bytes) -> bytes:
        """Minify JavaScript content"""
        js_text = content.decode('utf-8')
        
        # Simple JS minification (in production, use a proper JS minifier)
        import re
        
        # Remove single-line comments
        js_text = re.sub(r'//.*?$', '', js_text, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_text = re.sub(r'/\*.*?\*/', '', js_text, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js_text = re.sub(r'\s+', ' ', js_text)
        
        return js_text.encode('utf-8')
    
    def _minify_json(self, content: bytes) -> bytes:
        """Minify JSON content"""
        try:
            data = json.loads(content.decode('utf-8'))
            return json.dumps(data, separators=(',', ':')).encode('utf-8')
        except:
            return content
    
    def _add_version_to_path(self, file_path: str, version: str) -> str:
        """Add version hash to filename"""
        path = Path(file_path)
        name = path.stem
        ext = path.suffix
        parent = path.parent
        
        versioned_name = f"{name}.{version}{ext}"
        
        if parent == Path('.'):
            return versioned_name
        else:
            return str(parent / versioned_name)
    
    async def _cache_locally(self, file_path: str, content: bytes):
        """Cache file locally"""
        cache_path = self.local_cache_dir / file_path
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'wb') as f:
            f.write(content)
    
    async def _remove_from_local_cache(self, file_path: str):
        """Remove file from local cache"""
        cache_path = self.local_cache_dir / file_path
        if cache_path.exists():
            cache_path.unlink()
    
    def process_html_urls(self, html: str, cdn_map: Dict[str, str]) -> str:
        """Replace local URLs with CDN URLs in HTML"""
        for local_path, cdn_url in cdn_map.items():
            html = html.replace(f'src="{local_path}"', f'src="{cdn_url}"')
            html = html.replace(f"src='{local_path}'", f"src='{cdn_url}'")
            html = html.replace(f'href="{local_path}"', f'href="{cdn_url}"')
            html = html.replace(f"href='{local_path}'", f"href='{cdn_url}'")
        
        return html
    
    def get_cache_headers(self, file_type: str) -> Dict[str, str]:
        """Get appropriate cache headers for file type"""
        # Long cache for versioned assets
        if file_type in ['css', 'js', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'woff', 'woff2']:
            return {
                "Cache-Control": "public, max-age=31536000, immutable",
                "Expires": (datetime.now() + timedelta(days=365)).strftime("%a, %d %b %Y %H:%M:%S GMT")
            }
        
        # Medium cache for HTML
        elif file_type == 'html':
            return {
                "Cache-Control": "public, max-age=3600",
                "Expires": (datetime.now() + timedelta(hours=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
            }
        
        # Short cache for dynamic content
        else:
            return {
                "Cache-Control": "public, max-age=300",
                "Expires": (datetime.now() + timedelta(minutes=5)).strftime("%a, %d %b %Y %H:%M:%S GMT")
            }
    
    async def sync_with_cdn(self, local_dir: str, cdn_prefix: str = "") -> Dict[str, Any]:
        """Sync local directory with CDN"""
        local_path = Path(local_dir)
        
        # Get list of local files
        local_files = set()
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                local_files.add(str(relative_path))
        
        # Upload new and modified files
        uploaded = []
        updated = []
        
        for file_name in local_files:
            file_path = local_path / file_name
            cdn_path = os.path.join(cdn_prefix, file_name)
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Check if file needs updating (based on hash)
            file_hash = hashlib.md5(content).hexdigest()
            
            # Upload/update file
            cdn_url = await self.upload_file(cdn_path, content)
            
            if file_hash in cdn_url:  # New file
                uploaded.append(file_name)
            else:  # Updated file
                updated.append(file_name)
        
        return {
            "uploaded": uploaded,
            "updated": updated,
            "total_files": len(local_files)
        }

class ImageOptimizer:
    """Service for optimizing images before CDN upload"""
    
    @staticmethod
    async def optimize(
        image_data: bytes,
        format: str = 'webp',
        quality: int = 85,
        max_width: int = 2000,
        max_height: int = 2000
    ) -> bytes:
        """Optimize image for web delivery"""
        # In a real implementation, use PIL/Pillow
        # from PIL import Image
        # import io
        
        # img = Image.open(io.BytesIO(image_data))
        
        # # Resize if needed
        # img.thumbnail((max_width, max_height), Image.LANCZOS)
        
        # # Convert to WebP for better compression
        # output = io.BytesIO()
        # img.save(output, format=format.upper(), quality=quality, optimize=True)
        
        # return output.getvalue()
        
        # For now, return original
        return image_data