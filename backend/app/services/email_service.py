"""
Email Service
Handles transactional emails via SendGrid/Resend
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from jinja2 import Template

logger = logging.getLogger(__name__)

class EmailService:
    """
    Manages transactional email sending
    """
    
    def __init__(self):
        # Email provider configuration
        self.provider = os.getenv('EMAIL_PROVIDER', 'sendgrid')  # sendgrid or resend
        self.api_key = os.getenv('EMAIL_API_KEY', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@kenzysites.com.br')
        self.from_name = os.getenv('FROM_NAME', 'KenzySites')
        
        # API endpoints
        self.endpoints = {
            'sendgrid': 'https://api.sendgrid.com/v3/mail/send',
            'resend': 'https://api.resend.com/emails'
        }
        
        self.client = httpx.AsyncClient(timeout=30.0)
        self.templates = self._load_email_templates()
    
    def _load_email_templates(self) -> Dict[str, str]:
        """Load email templates"""
        
        return {
            'welcome': """
                <h1>Bem-vindo ao KenzySites, {{ client_name }}!</h1>
                <p>Seu site WordPress foi criado com sucesso!</p>
                <h2>Informações do seu site:</h2>
                <ul>
                    <li><strong>URL:</strong> <a href="https://{{ domain }}">https://{{ domain }}</a></li>
                    <li><strong>Admin:</strong> <a href="https://{{ domain }}/wp-admin">https://{{ domain }}/wp-admin</a></li>
                    <li><strong>Usuário:</strong> {{ admin_user }}</li>
                    <li><strong>Senha:</strong> {{ admin_password }}</li>
                </ul>
                <p>Guarde estas informações em local seguro!</p>
                <h3>Próximos passos:</h3>
                <ol>
                    <li>Acesse o painel administrativo</li>
                    <li>Personalize seu site</li>
                    <li>Configure seu domínio personalizado (opcional)</li>
                </ol>
                <p>Qualquer dúvida, entre em contato com nosso suporte.</p>
            """,
            
            'payment_warning': """
                <h1>Aviso de Pagamento Pendente</h1>
                <p>Olá {{ client_name }},</p>
                <p>Identificamos que existe um pagamento pendente para seu site <strong>{{ domain }}</strong>.</p>
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Valor:</strong> {{ amount }}</p>
                    <p><strong>Vencimento:</strong> {{ due_date }}</p>
                    <p><strong>Dias em atraso:</strong> {{ days_overdue }}</p>
                </div>
                <p>Para evitar a suspensão do seu site, regularize o pagamento o quanto antes.</p>
                <a href="{{ payment_link }}" style="display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">
                    Pagar Agora
                </a>
                <p><small>Seu site será suspenso automaticamente em {{ 7 - days_overdue }} dias caso o pagamento não seja realizado.</small></p>
            """,
            
            'site_suspended': """
                <h1>Site Suspenso</h1>
                <p>Olá {{ client_name }},</p>
                <p>Seu site <strong>{{ domain }}</strong> foi temporariamente suspenso devido a pagamento pendente.</p>
                <div style="background: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Valor pendente:</strong> {{ amount }}</p>
                    <p><strong>Dias em atraso:</strong> {{ days_overdue }}</p>
                </div>
                <p><strong>{{ reactivation_info }}</strong></p>
                <a href="{{ payment_link }}" style="display: inline-block; padding: 12px 24px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px;">
                    Regularizar Pagamento
                </a>
            """,
            
            'site_reactivated': """
                <h1>Site Reativado!</h1>
                <p>Olá {{ client_name }},</p>
                <p>Ótimas notícias! Seu pagamento foi confirmado e seu site <strong>{{ domain }}</strong> foi reativado com sucesso.</p>
                <p>Data da reativação: {{ reactivation_time }}</p>
                <p>Seu site já está disponível e funcionando normalmente.</p>
                <a href="https://{{ domain }}" style="display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">
                    Acessar Meu Site
                </a>
                <p>Obrigado por continuar conosco!</p>
            """,
            
            'final_warning': """
                <h1 style="color: #dc3545;">⚠️ AVISO FINAL - Ação Urgente Necessária</h1>
                <p>Olá {{ client_name }},</p>
                <p>Este é um <strong>AVISO FINAL</strong> sobre o pagamento pendente do seu site <strong>{{ domain }}</strong>.</p>
                <div style="background: #dc3545; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>ATENÇÃO:</strong> Seu site será PERMANENTEMENTE EXCLUÍDO em {{ deletion_date }} se o pagamento não for realizado.</p>
                </div>
                <p><strong>Valor pendente:</strong> {{ amount }}</p>
                <p><strong>Dias em atraso:</strong> {{ days_overdue }}</p>
                <a href="{{ payment_link }}" style="display: inline-block; padding: 15px 30px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; font-size: 18px;">
                    PAGAR AGORA E SALVAR MEU SITE
                </a>
                <p>Após a exclusão, todos os dados serão perdidos e não poderão ser recuperados.</p>
            """,
            
            'deletion_scheduled': """
                <h1>Site Agendado para Exclusão</h1>
                <p>Olá {{ client_name }},</p>
                <p>Seu site <strong>{{ domain }}</strong> está agendado para exclusão permanente em <strong>{{ deletion_date }}</strong>.</p>
                <h3>Backup dos seus dados:</h3>
                <p>Criamos um backup completo do seu site. Você pode baixá-lo através do link abaixo:</p>
                <a href="{{ backup_url }}" style="display: inline-block; padding: 12px 24px; background: #17a2b8; color: white; text-decoration: none; border-radius: 5px;">
                    Baixar Backup
                </a>
                <p><small>Este link expira em {{ backup_expiry }}</small></p>
                <h3>Última chance de reativação:</h3>
                <p>Você ainda pode evitar a exclusão realizando o pagamento:</p>
                <a href="{{ last_chance_payment }}" style="display: inline-block; padding: 12px 24px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px;">
                    Pagar e Reativar
                </a>
            """,
            
            'payment_received': """
                <h1>Pagamento Recebido</h1>
                <p>Olá {{ client_name }},</p>
                <p>Confirmamos o recebimento do seu pagamento!</p>
                <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Valor:</strong> {{ amount }}</p>
                    <p><strong>Data:</strong> {{ payment_date }}</p>
                    <p><strong>Forma de pagamento:</strong> {{ payment_method }}</p>
                </div>
                <p>Seu próximo vencimento será em <strong>{{ next_due_date }}</strong>.</p>
                <p>Obrigado pela confiança!</p>
            """
        }
    
    async def send_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send transactional email
        """
        
        try:
            # Render template with data
            template_name = email_data.get('template', 'default')
            template_data = email_data.get('data', {})
            
            if template_name in self.templates:
                template = Template(self.templates[template_name])
                html_content = template.render(**template_data)
            else:
                html_content = email_data.get('html', '')
            
            # Prepare email based on provider
            if self.provider == 'sendgrid':
                result = await self._send_via_sendgrid(
                    to=email_data['to'],
                    subject=email_data['subject'],
                    html=html_content,
                    text=email_data.get('text', '')
                )
            else:  # resend
                result = await self._send_via_resend(
                    to=email_data['to'],
                    subject=email_data['subject'],
                    html=html_content,
                    text=email_data.get('text', '')
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _send_via_sendgrid(
        self,
        to: str,
        subject: str,
        html: str,
        text: str = ''
    ) -> Dict[str, Any]:
        """
        Send email via SendGrid
        """
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'personalizations': [{
                'to': [{'email': to}],
                'subject': subject
            }],
            'from': {
                'email': self.from_email,
                'name': self.from_name
            },
            'content': [
                {'type': 'text/plain', 'value': text or 'Please view this email in HTML'},
                {'type': 'text/html', 'value': html}
            ]
        }
        
        try:
            response = await self.client.post(
                self.endpoints['sendgrid'],
                headers=headers,
                json=data
            )
            
            if response.status_code in [200, 202]:
                logger.info(f"Email sent successfully to {to}")
                return {'success': True, 'message_id': response.headers.get('X-Message-Id')}
            else:
                logger.error(f"SendGrid error: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _send_via_resend(
        self,
        to: str,
        subject: str,
        html: str,
        text: str = ''
    ) -> Dict[str, Any]:
        """
        Send email via Resend
        """
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'from': f'{self.from_name} <{self.from_email}>',
            'to': to,
            'subject': subject,
            'html': html,
            'text': text or 'Please view this email in HTML'
        }
        
        try:
            response = await self.client.post(
                self.endpoints['resend'],
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Email sent successfully to {to}")
                return {'success': True, 'message_id': result.get('id')}
            else:
                logger.error(f"Resend error: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Resend error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def send_bulk_emails(
        self,
        recipients: List[str],
        subject: str,
        template: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send bulk emails to multiple recipients
        """
        
        sent = 0
        failed = 0
        
        for recipient in recipients:
            email_data = {
                'to': recipient,
                'subject': subject,
                'template': template,
                'data': data
            }
            
            result = await self.send_email(email_data)
            
            if result.get('success'):
                sent += 1
            else:
                failed += 1
            
            # Rate limiting
            await asyncio.sleep(0.1)
        
        return {
            'success': True,
            'sent': sent,
            'failed': failed,
            'total': len(recipients)
        }

# Global instance
email_service = EmailService()