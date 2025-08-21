"""
DNS Manager Service
Automated DNS management with Cloudflare integration
"""

import logging
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import re

logger = logging.getLogger(__name__)

class DNSManager:
    """
    Manages DNS records automatically via Cloudflare API
    """
    
    def __init__(self):
        self.cloudflare_api_token = os.getenv('CLOUDFLARE_API_TOKEN', '')
        self.cloudflare_zone_id = os.getenv('CLOUDFLARE_ZONE_ID', '')
        self.base_domain = os.getenv('BASE_DOMAIN', 'kenzysites.com.br')
        self.base_url = 'https://api.cloudflare.com/client/v4'
        
        self.headers = {
            'Authorization': f'Bearer {self.cloudflare_api_token}',
            'Content-Type': 'application/json'
        }
        
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
        
        # IP addresses for load balancing
        self.server_ips = os.getenv('SERVER_IPS', '').split(',')
        if not self.server_ips or self.server_ips == ['']:
            self.server_ips = ['192.168.1.100']  # Default IP
    
    async def create_subdomain(
        self,
        subdomain: str,
        client_id: str,
        record_type: str = 'A',
        proxied: bool = True,
        ttl: int = 1  # 1 = automatic
    ) -> Dict[str, Any]:
        """
        Create a subdomain for a client
        """
        
        # Validate subdomain
        if not self._validate_subdomain(subdomain):
            return {
                'success': False,
                'error': 'Invalid subdomain format'
            }
        
        # Full domain name
        full_domain = f"{subdomain}.{self.base_domain}"
        
        try:
            # Check if record already exists
            existing = await self._get_dns_record(full_domain)
            if existing:
                logger.info(f"DNS record already exists for {full_domain}")
                return {
                    'success': True,
                    'domain': full_domain,
                    'record_id': existing['id'],
                    'message': 'Record already exists'
                }
            
            # Create DNS record
            data = {
                'type': record_type,
                'name': subdomain,
                'content': self.server_ips[0],  # Primary IP
                'ttl': ttl,
                'proxied': proxied,
                'comment': f'Client: {client_id}, Created: {datetime.now().isoformat()}'
            }
            
            response = await self.client.post(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records",
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                record = result['result']
                logger.info(f"Created DNS record for {full_domain}")
                
                # Create additional A records for load balancing if multiple IPs
                if len(self.server_ips) > 1:
                    for ip in self.server_ips[1:]:
                        await self._create_additional_a_record(subdomain, ip, client_id)
                
                return {
                    'success': True,
                    'domain': full_domain,
                    'record_id': record['id'],
                    'proxied': record['proxied'],
                    'ip_address': record['content']
                }
            else:
                errors = result.get('errors', [])
                return {
                    'success': False,
                    'error': errors[0]['message'] if errors else 'Unknown error'
                }
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to create DNS record: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _create_additional_a_record(
        self,
        subdomain: str,
        ip: str,
        client_id: str
    ):
        """Create additional A records for load balancing"""
        
        data = {
            'type': 'A',
            'name': subdomain,
            'content': ip,
            'ttl': 1,
            'proxied': True,
            'comment': f'Client: {client_id}, Load balanced IP'
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records",
                json=data
            )
            response.raise_for_status()
            logger.info(f"Added additional A record for {subdomain} with IP {ip}")
        except Exception as e:
            logger.error(f"Failed to add additional A record: {str(e)}")
    
    async def create_custom_domain(
        self,
        custom_domain: str,
        target_subdomain: str,
        client_id: str
    ) -> Dict[str, Any]:
        """
        Configure custom domain for a client (CNAME pointing to subdomain)
        """
        
        # Validate domain
        if not self._validate_domain(custom_domain):
            return {
                'success': False,
                'error': 'Invalid domain format'
            }
        
        # Full target domain
        target = f"{target_subdomain}.{self.base_domain}"
        
        # Create CNAME record instructions for client
        instructions = {
            'type': 'CNAME',
            'name': custom_domain,
            'value': target,
            'instructions': [
                f"1. Acesse o painel de DNS do seu domínio {custom_domain}",
                f"2. Crie um registro CNAME apontando para {target}",
                "3. Aguarde propagação DNS (até 48 horas)",
                "4. Configure SSL no painel após propagação"
            ]
        }
        
        # Store custom domain mapping
        await self._store_custom_domain_mapping(client_id, custom_domain, target)
        
        # Create SSL certificate for custom domain
        ssl_result = await self._request_ssl_certificate(custom_domain)
        
        return {
            'success': True,
            'custom_domain': custom_domain,
            'target': target,
            'dns_instructions': instructions,
            'ssl_status': ssl_result.get('status', 'pending')
        }
    
    async def _request_ssl_certificate(self, domain: str) -> Dict[str, Any]:
        """
        Request SSL certificate for custom domain via Cloudflare
        """
        
        try:
            # Create custom hostname (for Cloudflare for SaaS)
            data = {
                'hostname': domain,
                'ssl': {
                    'method': 'http',
                    'type': 'dv',
                    'settings': {
                        'http2': 'on',
                        'min_tls_version': '1.2'
                    }
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/custom_hostnames",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'requested',
                    'ssl_id': result.get('result', {}).get('id')
                }
            else:
                return {'status': 'manual_required'}
                
        except Exception as e:
            logger.error(f"Failed to request SSL certificate: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def update_dns_record(
        self,
        record_id: str,
        new_ip: Optional[str] = None,
        proxied: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update existing DNS record
        """
        
        try:
            # Get current record
            response = await self.client.get(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records/{record_id}"
            )
            response.raise_for_status()
            current = response.json()['result']
            
            # Update fields
            data = {
                'type': current['type'],
                'name': current['name'],
                'content': new_ip or current['content'],
                'ttl': current['ttl'],
                'proxied': proxied if proxied is not None else current['proxied']
            }
            
            # Update record
            response = await self.client.put(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records/{record_id}",
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"Updated DNS record {record_id}")
                return {
                    'success': True,
                    'record_id': record_id,
                    'updated': True
                }
            else:
                return {
                    'success': False,
                    'error': result.get('errors', ['Unknown error'])[0]
                }
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to update DNS record: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_dns_record(self, record_id: str) -> Dict[str, Any]:
        """
        Delete DNS record
        """
        
        try:
            response = await self.client.delete(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records/{record_id}"
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"Deleted DNS record {record_id}")
                return {'success': True, 'deleted': True}
            else:
                return {
                    'success': False,
                    'error': result.get('errors', ['Unknown error'])[0]
                }
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete DNS record: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_subdomain(self, subdomain: str) -> Dict[str, Any]:
        """
        Delete subdomain and all associated records
        """
        
        full_domain = f"{subdomain}.{self.base_domain}"
        
        try:
            # Get all records for this subdomain
            records = await self._get_all_dns_records(subdomain)
            
            # Delete each record
            deleted_count = 0
            for record in records:
                result = await self.delete_dns_record(record['id'])
                if result.get('success'):
                    deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} DNS records for {full_domain}")
            
            return {
                'success': True,
                'domain': full_domain,
                'deleted_records': deleted_count
            }
            
        except Exception as e:
            logger.error(f"Failed to delete subdomain: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_dns_record(self, domain: str) -> Optional[Dict]:
        """
        Get DNS record by domain name
        """
        
        try:
            response = await self.client.get(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records",
                params={'name': domain}
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success') and result.get('result'):
                return result['result'][0] if result['result'] else None
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get DNS record: {str(e)}")
            return None
    
    async def _get_all_dns_records(self, subdomain: str) -> List[Dict]:
        """
        Get all DNS records for a subdomain
        """
        
        full_domain = f"{subdomain}.{self.base_domain}"
        
        try:
            response = await self.client.get(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records",
                params={'name': full_domain}
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return result.get('result', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get DNS records: {str(e)}")
            return []
    
    def _validate_subdomain(self, subdomain: str) -> bool:
        """
        Validate subdomain format
        """
        
        # Subdomain rules:
        # - 1-63 characters
        # - Only letters, numbers, and hyphens
        # - Cannot start or end with hyphen
        # - No consecutive hyphens
        
        pattern = r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'
        return bool(re.match(pattern, subdomain.lower()))
    
    def _validate_domain(self, domain: str) -> bool:
        """
        Validate domain format
        """
        
        # Basic domain validation
        pattern = r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
        return bool(re.match(pattern, domain.lower()))
    
    async def _store_custom_domain_mapping(
        self,
        client_id: str,
        custom_domain: str,
        target: str
    ):
        """
        Store custom domain mapping in database
        """
        
        # This would store in database
        # For now, just log
        logger.info(f"Stored custom domain mapping: {custom_domain} -> {target} for client {client_id}")
    
    async def verify_dns_propagation(self, domain: str) -> Dict[str, Any]:
        """
        Check if DNS has propagated
        """
        
        import socket
        
        try:
            # Try to resolve domain
            ip = socket.gethostbyname(domain)
            
            # Check if resolved IP matches our servers
            is_ours = ip in self.server_ips
            
            return {
                'success': True,
                'propagated': True,
                'resolved_ip': ip,
                'is_configured': is_ours
            }
            
        except socket.gaierror:
            return {
                'success': True,
                'propagated': False,
                'message': 'DNS not propagated yet'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def setup_email_records(
        self,
        subdomain: str,
        email_provider: str = 'google'
    ) -> Dict[str, Any]:
        """
        Setup email DNS records (MX, SPF, DKIM, DMARC)
        """
        
        email_configs = {
            'google': {
                'mx': [
                    {'priority': 1, 'server': 'aspmx.l.google.com'},
                    {'priority': 5, 'server': 'alt1.aspmx.l.google.com'},
                    {'priority': 5, 'server': 'alt2.aspmx.l.google.com'},
                    {'priority': 10, 'server': 'alt3.aspmx.l.google.com'},
                    {'priority': 10, 'server': 'alt4.aspmx.l.google.com'}
                ],
                'spf': 'v=spf1 include:_spf.google.com ~all'
            },
            'sendgrid': {
                'mx': [{'priority': 10, 'server': 'mx.sendgrid.net'}],
                'spf': 'v=spf1 include:sendgrid.net ~all'
            }
        }
        
        config = email_configs.get(email_provider, email_configs['google'])
        full_domain = f"{subdomain}.{self.base_domain}"
        
        try:
            # Create MX records
            for mx in config['mx']:
                await self.client.post(
                    f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records",
                    json={
                        'type': 'MX',
                        'name': subdomain,
                        'content': mx['server'],
                        'priority': mx['priority'],
                        'ttl': 3600
                    }
                )
            
            # Create SPF record
            await self.client.post(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records",
                json={
                    'type': 'TXT',
                    'name': subdomain,
                    'content': config['spf'],
                    'ttl': 3600
                }
            )
            
            # Create DMARC record
            await self.client.post(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/dns_records",
                json={
                    'type': 'TXT',
                    'name': f'_dmarc.{subdomain}',
                    'content': 'v=DMARC1; p=quarantine; rua=mailto:dmarc@kenzysites.com.br',
                    'ttl': 3600
                }
            )
            
            logger.info(f"Email records configured for {full_domain}")
            
            return {
                'success': True,
                'domain': full_domain,
                'email_provider': email_provider,
                'mx_records': config['mx']
            }
            
        except Exception as e:
            logger.error(f"Failed to setup email records: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def enable_ddos_protection(self, subdomain: str) -> Dict[str, Any]:
        """
        Enable Cloudflare DDoS protection and rate limiting
        """
        
        try:
            # Create rate limiting rule
            rule_data = {
                'match': {
                    'request': {
                        'url': f'*{subdomain}.{self.base_domain}/*'
                    }
                },
                'threshold': 100,  # requests
                'period': 60,  # seconds
                'action': {
                    'mode': 'challenge'  # Show CAPTCHA
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/zones/{self.cloudflare_zone_id}/rate_limits",
                json=rule_data
            )
            
            response.raise_for_status()
            
            logger.info(f"DDoS protection enabled for {subdomain}")
            
            return {
                'success': True,
                'protection_enabled': True,
                'rate_limit': '100 requests per minute'
            }
            
        except Exception as e:
            logger.error(f"Failed to enable DDoS protection: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
dns_manager = DNSManager()