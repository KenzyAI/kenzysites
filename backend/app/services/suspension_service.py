"""
Automatic Suspension Service
Handles automatic site suspension for overdue payments
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json

from app.services.wordpress_provisioner import wordpress_provisioner
from app.services.asaas_integration import asaas, PaymentStatus
from app.services.email_service import email_service
from app.services.dns_manager import dns_manager

logger = logging.getLogger(__name__)

class SuspensionStatus(Enum):
    ACTIVE = "active"
    WARNING_SENT = "warning_sent"
    SUSPENDED = "suspended"
    FINAL_WARNING = "final_warning"
    SCHEDULED_DELETION = "scheduled_deletion"
    DELETED = "deleted"

class SuspensionService:
    """
    Manages automatic suspension and reactivation of WordPress sites
    """
    
    def __init__(self):
        self.grace_periods = {
            'first_warning': 3,    # Days after due date
            'suspension': 7,       # Days after due date
            'final_warning': 15,   # Days after due date
            'deletion': 30        # Days after due date
        }
        
        # In production, this would use Redis or database
        self.suspension_state = {}
    
    async def check_overdue_payments(self) -> List[Dict[str, Any]]:
        """
        Check all active subscriptions for overdue payments
        This should run daily via cron job
        """
        
        overdue_sites = []
        
        try:
            # Get all active clients from database
            # For now, using mock data
            clients = await self._get_all_active_clients()
            
            for client in clients:
                # Check payment status with Asaas
                subscription_id = client.get('subscription_id')
                if not subscription_id:
                    continue
                
                # Get invoices from Asaas
                invoices_result = await asaas.get_subscription_invoices(
                    subscription_id,
                    status=PaymentStatus.OVERDUE
                )
                
                if invoices_result.get('success') and invoices_result.get('invoices'):
                    for invoice in invoices_result['invoices']:
                        due_date = datetime.fromisoformat(invoice['dueDate'])
                        days_overdue = (datetime.now() - due_date).days
                        
                        overdue_sites.append({
                            'client_id': client['id'],
                            'client_name': client['name'],
                            'domain': client['domain'],
                            'invoice_id': invoice['id'],
                            'amount': invoice['value'],
                            'due_date': due_date,
                            'days_overdue': days_overdue,
                            'current_status': client.get('status', SuspensionStatus.ACTIVE.value)
                        })
            
            # Process each overdue site
            for site in overdue_sites:
                await self._process_overdue_site(site)
            
            logger.info(f"Processed {len(overdue_sites)} overdue sites")
            return overdue_sites
            
        except Exception as e:
            logger.error(f"Error checking overdue payments: {str(e)}")
            return []
    
    async def _process_overdue_site(self, site: Dict[str, Any]):
        """
        Process an overdue site based on days overdue
        """
        
        client_id = site['client_id']
        days_overdue = site['days_overdue']
        current_status = SuspensionStatus(site['current_status'])
        
        try:
            # Day 3: Send first warning
            if days_overdue >= self.grace_periods['first_warning'] and current_status == SuspensionStatus.ACTIVE:
                await self._send_first_warning(site)
                await self._update_site_status(client_id, SuspensionStatus.WARNING_SENT)
            
            # Day 7: Suspend site
            elif days_overdue >= self.grace_periods['suspension'] and current_status == SuspensionStatus.WARNING_SENT:
                await self._suspend_site(site)
                await self._update_site_status(client_id, SuspensionStatus.SUSPENDED)
            
            # Day 15: Send final warning
            elif days_overdue >= self.grace_periods['final_warning'] and current_status == SuspensionStatus.SUSPENDED:
                await self._send_final_warning(site)
                await self._update_site_status(client_id, SuspensionStatus.FINAL_WARNING)
            
            # Day 30: Schedule deletion
            elif days_overdue >= self.grace_periods['deletion'] and current_status == SuspensionStatus.FINAL_WARNING:
                await self._schedule_deletion(site)
                await self._update_site_status(client_id, SuspensionStatus.SCHEDULED_DELETION)
            
        except Exception as e:
            logger.error(f"Error processing overdue site {client_id}: {str(e)}")
    
    async def _send_first_warning(self, site: Dict[str, Any]):
        """
        Send first warning email (Day 3)
        """
        
        email_data = {
            'to': site.get('email'),
            'subject': f"⚠️ Aviso de Pagamento Pendente - {site['domain']}",
            'template': 'payment_warning',
            'data': {
                'client_name': site['client_name'],
                'domain': site['domain'],
                'amount': f"R$ {site['amount']:.2f}",
                'due_date': site['due_date'].strftime('%d/%m/%Y'),
                'days_overdue': site['days_overdue'],
                'payment_link': f"https://portal.kenzysites.com.br/payment/{site['invoice_id']}",
                'warning_type': 'first'
            }
        }
        
        await email_service.send_email(email_data)
        logger.info(f"First warning sent to {site['client_id']}")
    
    async def _suspend_site(self, site: Dict[str, Any]):
        """
        Suspend WordPress site (Day 7)
        """
        
        client_id = site['client_id']
        
        try:
            # Suspend site in Kubernetes
            suspension_result = await wordpress_provisioner.suspend_site(client_id)
            
            if suspension_result.get('success'):
                # Create suspension page
                await self._create_suspension_page(site)
                
                # Send suspension email
                email_data = {
                    'to': site.get('email'),
                    'subject': f"🔴 Site Suspenso - {site['domain']}",
                    'template': 'site_suspended',
                    'data': {
                        'client_name': site['client_name'],
                        'domain': site['domain'],
                        'amount': f"R$ {site['amount']:.2f}",
                        'days_overdue': site['days_overdue'],
                        'payment_link': f"https://portal.kenzysites.com.br/payment/{site['invoice_id']}",
                        'reactivation_info': 'Seu site será reativado automaticamente após o pagamento.'
                    }
                }
                
                await email_service.send_email(email_data)
                logger.info(f"Site suspended: {client_id}")
            
        except Exception as e:
            logger.error(f"Failed to suspend site {client_id}: {str(e)}")
    
    async def _create_suspension_page(self, site: Dict[str, Any]):
        """
        Create a suspension page that replaces the site
        """
        
        suspension_html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Site Suspenso - {site['domain']}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                }}
                .container {{
                    text-align: center;
                    padding: 2rem;
                    max-width: 500px;
                }}
                h1 {{
                    font-size: 3rem;
                    margin-bottom: 1rem;
                }}
                .icon {{
                    font-size: 5rem;
                    margin-bottom: 1rem;
                }}
                .message {{
                    font-size: 1.2rem;
                    margin-bottom: 2rem;
                    opacity: 0.9;
                }}
                .button {{
                    display: inline-block;
                    padding: 1rem 2rem;
                    background: white;
                    color: #667eea;
                    text-decoration: none;
                    border-radius: 50px;
                    font-weight: bold;
                    transition: transform 0.3s;
                }}
                .button:hover {{
                    transform: scale(1.05);
                }}
                .info {{
                    margin-top: 2rem;
                    font-size: 0.9rem;
                    opacity: 0.7;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🔒</div>
                <h1>Site Suspenso</h1>
                <div class="message">
                    Este site foi temporariamente suspenso devido a pagamento pendente.
                </div>
                <a href="https://portal.kenzysites.com.br/payment/{site['invoice_id']}" class="button">
                    Regularizar Pagamento
                </a>
                <div class="info">
                    <p>Valor pendente: R$ {site['amount']:.2f}</p>
                    <p>Vencimento: {site['due_date'].strftime('%d/%m/%Y')}</p>
                    <p>Após o pagamento, o site será reativado automaticamente em até 15 minutos.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # In production, this would be served by nginx when site is suspended
        # Store suspension page in a static location
        suspension_path = f"/var/www/suspended/{site['client_id']}/index.html"
        
        # This would write the file to the appropriate location
        logger.info(f"Suspension page created for {site['domain']}")
    
    async def _send_final_warning(self, site: Dict[str, Any]):
        """
        Send final warning before deletion (Day 15)
        """
        
        email_data = {
            'to': site.get('email'),
            'subject': f"⚠️ AVISO FINAL - Site será excluído - {site['domain']}",
            'template': 'final_warning',
            'data': {
                'client_name': site['client_name'],
                'domain': site['domain'],
                'amount': f"R$ {site['amount']:.2f}",
                'days_overdue': site['days_overdue'],
                'deletion_date': (datetime.now() + timedelta(days=15)).strftime('%d/%m/%Y'),
                'payment_link': f"https://portal.kenzysites.com.br/payment/{site['invoice_id']}",
                'urgent': True
            }
        }
        
        await email_service.send_email(email_data)
        
        # Also send WhatsApp if configured
        if site.get('whatsapp'):
            await self._send_whatsapp_warning(site)
        
        logger.info(f"Final warning sent to {site['client_id']}")
    
    async def _schedule_deletion(self, site: Dict[str, Any]):
        """
        Schedule site for deletion (Day 30)
        """
        
        client_id = site['client_id']
        
        try:
            # Create backup before deletion
            from app.services.backup_service import backup_service
            
            backup_result = await backup_service.backup_wordpress_site(
                client_id,
                backup_type='final',
                include_uploads=True,
                include_plugins=True,
                include_themes=True
            )
            
            if backup_result.get('success'):
                # Schedule deletion for next maintenance window
                deletion_date = datetime.now() + timedelta(days=1)
                
                # Store deletion schedule
                self.suspension_state[client_id] = {
                    'status': SuspensionStatus.SCHEDULED_DELETION.value,
                    'deletion_date': deletion_date.isoformat(),
                    'backup_id': backup_result['backup_id'],
                    'backup_url': backup_result['url']
                }
                
                # Send final email with backup link
                email_data = {
                    'to': site.get('email'),
                    'subject': f"🔴 Site agendado para exclusão - {site['domain']}",
                    'template': 'deletion_scheduled',
                    'data': {
                        'client_name': site['client_name'],
                        'domain': site['domain'],
                        'deletion_date': deletion_date.strftime('%d/%m/%Y'),
                        'backup_url': backup_result['url'],
                        'backup_expiry': (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
                        'last_chance_payment': f"https://portal.kenzysites.com.br/payment/{site['invoice_id']}"
                    }
                }
                
                await email_service.send_email(email_data)
                logger.info(f"Deletion scheduled for {client_id}")
            
        except Exception as e:
            logger.error(f"Failed to schedule deletion for {client_id}: {str(e)}")
    
    async def reactivate_site(self, client_id: str, payment_id: str) -> Dict[str, Any]:
        """
        Reactivate a suspended site after payment
        """
        
        try:
            # Verify payment with Asaas
            payment_status = await asaas.get_payment_status(payment_id)
            
            if payment_status.get('status') not in [PaymentStatus.CONFIRMED.value, PaymentStatus.RECEIVED.value]:
                return {
                    'success': False,
                    'error': 'Payment not confirmed'
                }
            
            # Resume site in Kubernetes
            resume_result = await wordpress_provisioner.resume_site(client_id)
            
            if resume_result.get('success'):
                # Update site status
                await self._update_site_status(client_id, SuspensionStatus.ACTIVE)
                
                # Remove from suspension state
                if client_id in self.suspension_state:
                    del self.suspension_state[client_id]
                
                # Send reactivation email
                site_info = await self._get_site_info(client_id)
                
                email_data = {
                    'to': site_info.get('email'),
                    'subject': f"✅ Site Reativado - {site_info['domain']}",
                    'template': 'site_reactivated',
                    'data': {
                        'client_name': site_info['name'],
                        'domain': site_info['domain'],
                        'reactivation_time': datetime.now().strftime('%d/%m/%Y %H:%M')
                    }
                }
                
                await email_service.send_email(email_data)
                
                logger.info(f"Site reactivated: {client_id}")
                
                return {
                    'success': True,
                    'message': 'Site reactivated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to resume site'
                }
                
        except Exception as e:
            logger.error(f"Failed to reactivate site {client_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_scheduled_deletions(self):
        """
        Execute scheduled deletions
        This should run daily
        """
        
        deletions_executed = []
        
        for client_id, state in self.suspension_state.items():
            if state['status'] == SuspensionStatus.SCHEDULED_DELETION.value:
                deletion_date = datetime.fromisoformat(state['deletion_date'])
                
                if datetime.now() >= deletion_date:
                    try:
                        # Delete the site
                        delete_result = await wordpress_provisioner.delete_site(client_id)
                        
                        if delete_result.get('success'):
                            # Delete DNS records
                            site_info = await self._get_site_info(client_id)
                            subdomain = site_info['domain'].split('.')[0]
                            await dns_manager.delete_subdomain(subdomain)
                            
                            # Cancel subscription in Asaas
                            if site_info.get('subscription_id'):
                                await asaas.cancel_subscription(
                                    site_info['subscription_id'],
                                    reason='Non-payment - 30 days overdue'
                                )
                            
                            # Update status
                            await self._update_site_status(client_id, SuspensionStatus.DELETED)
                            
                            deletions_executed.append(client_id)
                            logger.info(f"Site deleted: {client_id}")
                    
                    except Exception as e:
                        logger.error(f"Failed to delete site {client_id}: {str(e)}")
        
        # Remove deleted sites from suspension state
        for client_id in deletions_executed:
            del self.suspension_state[client_id]
        
        logger.info(f"Executed {len(deletions_executed)} scheduled deletions")
        return deletions_executed
    
    async def get_suspension_dashboard(self) -> Dict[str, Any]:
        """
        Get suspension dashboard data for admin
        """
        
        stats = {
            'total_active': 0,
            'warnings_sent': 0,
            'suspended': 0,
            'scheduled_deletion': 0,
            'sites': []
        }
        
        # Get all sites and their status
        clients = await self._get_all_clients()
        
        for client in clients:
            status = SuspensionStatus(client.get('status', SuspensionStatus.ACTIVE.value))
            
            if status == SuspensionStatus.ACTIVE:
                stats['total_active'] += 1
            elif status == SuspensionStatus.WARNING_SENT:
                stats['warnings_sent'] += 1
            elif status == SuspensionStatus.SUSPENDED:
                stats['suspended'] += 1
            elif status == SuspensionStatus.SCHEDULED_DELETION:
                stats['scheduled_deletion'] += 1
            
            # Add to sites list if not active
            if status != SuspensionStatus.ACTIVE:
                stats['sites'].append({
                    'client_id': client['id'],
                    'name': client['name'],
                    'domain': client['domain'],
                    'status': status.value,
                    'days_overdue': client.get('days_overdue', 0),
                    'amount_due': client.get('amount_due', 0)
                })
        
        return stats
    
    async def _update_site_status(self, client_id: str, status: SuspensionStatus):
        """
        Update site status in database
        """
        
        # In production, this would update the database
        logger.info(f"Updated site {client_id} status to {status.value}")
    
    async def _get_all_active_clients(self) -> List[Dict]:
        """
        Get all active clients from database
        """
        
        # In production, this would query the database
        # Mock data for now
        return [
            {
                'id': 'client_001',
                'name': 'Restaurante do João',
                'domain': 'restaurantedojoao.kenzysites.com.br',
                'email': 'joao@restaurante.com',
                'subscription_id': 'sub_001',
                'status': 'active'
            }
        ]
    
    async def _get_all_clients(self) -> List[Dict]:
        """
        Get all clients from database
        """
        
        # In production, this would query the database
        return await self._get_all_active_clients()
    
    async def _get_site_info(self, client_id: str) -> Dict:
        """
        Get site information
        """
        
        # In production, this would query the database
        return {
            'id': client_id,
            'name': 'Cliente',
            'domain': f'{client_id}.kenzysites.com.br',
            'email': 'cliente@email.com',
            'subscription_id': 'sub_001'
        }
    
    async def _send_whatsapp_warning(self, site: Dict[str, Any]):
        """
        Send WhatsApp warning message
        """
        
        # This would integrate with WhatsApp Business API
        logger.info(f"WhatsApp warning would be sent to {site.get('whatsapp')}")

# Global instance
suspension_service = SuspensionService()

# Cron job functions to be called by scheduler
async def daily_suspension_check():
    """
    Daily cron job to check overdue payments
    Should run at 10:00 AM every day
    """
    
    logger.info("Starting daily suspension check")
    
    # Check overdue payments
    overdue_sites = await suspension_service.check_overdue_payments()
    
    # Execute scheduled deletions
    deletions = await suspension_service.execute_scheduled_deletions()
    
    logger.info(f"Daily suspension check completed. Overdue: {len(overdue_sites)}, Deleted: {len(deletions)}")
    
    return {
        'overdue_sites': len(overdue_sites),
        'deletions_executed': len(deletions)
    }