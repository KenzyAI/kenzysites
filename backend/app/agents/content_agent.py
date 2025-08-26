"""
Content Agent
Responsible for generating and optimizing content
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ContentAgent:
    """
    AI Agent specialized in content generation and optimization
    """
    
    def __init__(self, ai_provider=None):
        self.ai_provider = ai_provider
        self.name = "ContentAgent"
        self.capabilities = [
            "generate_headlines",
            "write_descriptions",
            "create_cta_text",
            "generate_about_text",
            "create_service_descriptions",
            "write_testimonials",
            "generate_faq",
            "localize_content"
        ]
    
    async def generate_content(
        self,
        business_data: Dict[str, Any],
        content_type: str,
        language: str = "pt-BR",
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate specific type of content
        
        Args:
            business_data: Business information
            content_type: Type of content to generate
            language: Target language
            tone: Content tone (professional, casual, friendly, etc.)
            
        Returns:
            Generated content
        """
        
        logger.info(f"Generating {content_type} content for {business_data.get('business_name')}")
        
        if content_type == "hero":
            return await self._generate_hero_content(business_data, tone)
        elif content_type == "about":
            return await self._generate_about_content(business_data, tone)
        elif content_type == "services":
            return await self._generate_services_content(business_data, tone)
        elif content_type == "cta":
            return await self._generate_cta_content(business_data, tone)
        elif content_type == "testimonials":
            return await self._generate_testimonials(business_data)
        elif content_type == "faq":
            return await self._generate_faq(business_data)
        else:
            return await self._generate_generic_content(business_data, content_type, tone)
    
    async def _generate_hero_content(
        self,
        business_data: Dict[str, Any],
        tone: str
    ) -> Dict[str, Any]:
        """Generate hero section content"""
        
        business_name = business_data.get("business_name", "")
        industry = business_data.get("industry", "")
        description = business_data.get("description", "")
        
        # Generate using AI or use templates
        if self.ai_provider:
            prompt = f"""
            Gere um título e subtítulo para a seção hero de um site.
            Negócio: {business_name}
            Indústria: {industry}
            Descrição: {description}
            Tom: {tone}
            Língua: Português brasileiro
            
            Retorne em formato JSON:
            {{
                "headline": "título principal",
                "subheadline": "subtítulo",
                "cta_primary": "texto do botão principal",
                "cta_secondary": "texto do botão secundário"
            }}
            """
            
            # Call AI provider (placeholder)
            result = await self._call_ai(prompt)
            return result
        else:
            # Use industry-specific templates
            templates = {
                "restaurant": {
                    "headline": f"Bem-vindo ao {business_name}",
                    "subheadline": "Sabores únicos que encantam seu paladar",
                    "cta_primary": "Ver Cardápio",
                    "cta_secondary": "Fazer Reserva"
                },
                "healthcare": {
                    "headline": f"{business_name} - Cuidando da Sua Saúde",
                    "subheadline": "Atendimento humanizado com excelência médica",
                    "cta_primary": "Agendar Consulta",
                    "cta_secondary": "Nossos Serviços"
                },
                "ecommerce": {
                    "headline": f"Compre com Segurança no {business_name}",
                    "subheadline": "Os melhores produtos com entrega rápida",
                    "cta_primary": "Ver Produtos",
                    "cta_secondary": "Ofertas Especiais"
                },
                "services": {
                    "headline": f"{business_name} - Soluções Profissionais",
                    "subheadline": "Qualidade e eficiência em cada serviço",
                    "cta_primary": "Solicitar Orçamento",
                    "cta_secondary": "Conhecer Serviços"
                },
                "education": {
                    "headline": f"Transforme seu Futuro com {business_name}",
                    "subheadline": "Educação de qualidade ao seu alcance",
                    "cta_primary": "Inscreva-se Agora",
                    "cta_secondary": "Nossos Cursos"
                }
            }
            
            return templates.get(industry, templates["services"])
    
    async def _generate_about_content(
        self,
        business_data: Dict[str, Any],
        tone: str
    ) -> Dict[str, Any]:
        """Generate about section content"""
        
        business_name = business_data.get("business_name", "")
        description = business_data.get("description", "")
        industry = business_data.get("industry", "")
        
        # Industry-specific about templates
        templates = {
            "restaurant": f"""
            O {business_name} é mais do que um restaurante, é uma experiência gastronômica única.
            Com pratos cuidadosamente preparados por nossos chefs experientes, oferecemos uma 
            combinação perfeita de sabores tradicionais e inovação culinária. Nosso ambiente 
            acolhedor e atendimento excepcional tornam cada visita memorável.
            """,
            "healthcare": f"""
            No {business_name}, nossa missão é proporcionar cuidados de saúde excepcionais 
            com um toque humano. Nossa equipe de profissionais altamente qualificados está 
            comprometida em oferecer tratamentos personalizados, utilizando tecnologia de 
            ponta e as melhores práticas médicas para garantir seu bem-estar.
            """,
            "ecommerce": f"""
            O {business_name} nasceu com o objetivo de facilitar suas compras online, 
            oferecendo produtos de qualidade com os melhores preços do mercado. Nossa 
            plataforma segura e intuitiva, combinada com entrega rápida e atendimento 
            dedicado, garante uma experiência de compra excepcional.
            """,
            "services": f"""
            Com anos de experiência no mercado, o {business_name} se destaca pela 
            excelência em seus serviços e compromisso com a satisfação do cliente. 
            Nossa equipe especializada trabalha com dedicação para entregar soluções 
            eficientes e personalizadas que superam expectativas.
            """,
            "education": f"""
            O {business_name} é uma instituição comprometida com a transformação de 
            vidas através da educação. Oferecemos programas educacionais inovadores, 
            professores qualificados e infraestrutura moderna para proporcionar a 
            melhor experiência de aprendizado aos nossos alunos.
            """
        }
        
        about_text = templates.get(industry, templates["services"])
        
        # Add custom description if provided
        if description:
            about_text = f"{about_text}\n\n{description}"
        
        return {
            "title": f"Sobre o {business_name}",
            "content": about_text.strip(),
            "mission": self._generate_mission(business_data),
            "vision": self._generate_vision(business_data),
            "values": self._generate_values(business_data)
        }
    
    async def _generate_services_content(
        self,
        business_data: Dict[str, Any],
        tone: str
    ) -> Dict[str, Any]:
        """Generate services section content"""
        
        services = business_data.get("services", [])
        industry = business_data.get("industry", "")
        
        if not services:
            # Generate default services based on industry
            services = self._get_default_services(industry)
        
        service_items = []
        for service in services:
            if isinstance(service, str):
                service_items.append({
                    "title": service,
                    "description": self._generate_service_description(service, industry),
                    "icon": self._get_service_icon(service)
                })
            else:
                service_items.append(service)
        
        return {
            "title": "Nossos Serviços",
            "subtitle": "Conheça tudo o que oferecemos para você",
            "services": service_items
        }
    
    async def _generate_cta_content(
        self,
        business_data: Dict[str, Any],
        tone: str
    ) -> Dict[str, Any]:
        """Generate call-to-action content"""
        
        business_name = business_data.get("business_name", "")
        whatsapp = business_data.get("whatsapp", "")
        
        cta_templates = {
            "professional": {
                "title": "Pronto para Começar?",
                "subtitle": f"Entre em contato com o {business_name} hoje mesmo",
                "button_text": "Fale Conosco",
                "secondary_text": "Solicitar Orçamento"
            },
            "casual": {
                "title": "Vamos Conversar?",
                "subtitle": "Estamos aqui para ajudar você!",
                "button_text": "Chamar no WhatsApp" if whatsapp else "Entrar em Contato",
                "secondary_text": "Saber Mais"
            },
            "friendly": {
                "title": "Que tal nos conhecer melhor?",
                "subtitle": "Adoraríamos ouvir de você!",
                "button_text": "Dizer Olá",
                "secondary_text": "Visitar Loja"
            },
            "urgent": {
                "title": "Oferta por Tempo Limitado!",
                "subtitle": "Não perca esta oportunidade única",
                "button_text": "Aproveitar Agora",
                "secondary_text": "Ver Condições"
            }
        }
        
        return cta_templates.get(tone, cta_templates["professional"])
    
    async def _generate_testimonials(
        self,
        business_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate testimonial content"""
        
        industry = business_data.get("industry", "")
        
        # Industry-specific testimonial templates
        testimonials = {
            "restaurant": [
                {
                    "author": "Maria Silva",
                    "role": "Cliente Frequente",
                    "content": "A melhor experiência gastronômica da cidade! Pratos deliciosos e atendimento impecável.",
                    "rating": 5
                },
                {
                    "author": "João Santos",
                    "role": "Food Blogger",
                    "content": "Sabores autênticos e ambiente acolhedor. Recomendo fortemente!",
                    "rating": 5
                },
                {
                    "author": "Ana Costa",
                    "role": "Cliente",
                    "content": "Sempre volto aqui com minha família. Qualidade consistente e preços justos.",
                    "rating": 5
                }
            ],
            "healthcare": [
                {
                    "author": "Pedro Oliveira",
                    "role": "Paciente",
                    "content": "Profissionais extremamente competentes e atenciosos. Me senti muito bem cuidado.",
                    "rating": 5
                },
                {
                    "author": "Lucia Ferreira",
                    "role": "Paciente",
                    "content": "Clínica moderna com equipamentos de ponta. Excelente atendimento!",
                    "rating": 5
                },
                {
                    "author": "Carlos Mendes",
                    "role": "Paciente",
                    "content": "Equipe muito profissional e ambiente acolhedor. Superou minhas expectativas.",
                    "rating": 5
                }
            ],
            "ecommerce": [
                {
                    "author": "Fernanda Lima",
                    "role": "Cliente Verificado",
                    "content": "Entrega super rápida e produtos de excelente qualidade. Muito satisfeita!",
                    "rating": 5
                },
                {
                    "author": "Roberto Alves",
                    "role": "Cliente",
                    "content": "Ótimos preços e atendimento ao cliente excepcional. Recomendo!",
                    "rating": 5
                },
                {
                    "author": "Patricia Souza",
                    "role": "Cliente VIP",
                    "content": "Compro sempre aqui. Confiança total na loja e nos produtos.",
                    "rating": 5
                }
            ]
        }
        
        return testimonials.get(industry, testimonials["ecommerce"])
    
    async def _generate_faq(
        self,
        business_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate FAQ content"""
        
        industry = business_data.get("industry", "")
        whatsapp = business_data.get("whatsapp", "")
        pix = business_data.get("accept_pix", False)
        
        base_faq = [
            {
                "question": "Qual o horário de funcionamento?",
                "answer": "Funcionamos de segunda a sexta das 8h às 18h, e aos sábados das 8h às 12h."
            },
            {
                "question": "Como posso entrar em contato?",
                "answer": f"Você pode nos contatar através do {'WhatsApp, ' if whatsapp else ''}telefone, email ou formulário de contato em nosso site."
            },
            {
                "question": "Onde vocês estão localizados?",
                "answer": "Estamos localizados no centro da cidade. Veja nosso endereço completo na página de contato."
            }
        ]
        
        if pix:
            base_faq.append({
                "question": "Vocês aceitam pagamento via PIX?",
                "answer": "Sim! Aceitamos PIX para sua comodidade. É rápido, seguro e sem taxas adicionais."
            })
        
        # Add industry-specific FAQs
        industry_faq = {
            "restaurant": [
                {
                    "question": "Vocês fazem delivery?",
                    "answer": "Sim, fazemos delivery para toda a região. Consulte nossa área de entrega."
                },
                {
                    "question": "É necessário fazer reserva?",
                    "answer": "Recomendamos reserva, especialmente aos finais de semana, mas também aceitamos walk-ins."
                }
            ],
            "healthcare": [
                {
                    "question": "Vocês aceitam convênio?",
                    "answer": "Sim, trabalhamos com os principais convênios. Entre em contato para verificar o seu."
                },
                {
                    "question": "Como agendar uma consulta?",
                    "answer": "Você pode agendar pelo WhatsApp, telefone ou através do nosso sistema online."
                }
            ],
            "ecommerce": [
                {
                    "question": "Qual o prazo de entrega?",
                    "answer": "O prazo varia de acordo com sua localização, geralmente entre 3 a 7 dias úteis."
                },
                {
                    "question": "Posso trocar ou devolver produtos?",
                    "answer": "Sim, você tem até 7 dias após o recebimento para solicitar troca ou devolução."
                }
            ]
        }
        
        if industry in industry_faq:
            base_faq.extend(industry_faq[industry])
        
        return base_faq
    
    def _generate_mission(self, business_data: Dict[str, Any]) -> str:
        """Generate mission statement"""
        
        business_name = business_data.get("business_name", "")
        industry = business_data.get("industry", "")
        
        missions = {
            "restaurant": f"Proporcionar experiências gastronômicas memoráveis através de pratos excepcionais e atendimento caloroso.",
            "healthcare": f"Oferecer cuidados de saúde de excelência, priorizando o bem-estar e a qualidade de vida de nossos pacientes.",
            "ecommerce": f"Facilitar o acesso a produtos de qualidade, proporcionando uma experiência de compra segura e satisfatória.",
            "services": f"Entregar soluções eficientes e inovadoras que agregam valor real aos nossos clientes.",
            "education": f"Transformar vidas através da educação de qualidade, formando profissionais preparados para o futuro."
        }
        
        return missions.get(industry, missions["services"])
    
    def _generate_vision(self, business_data: Dict[str, Any]) -> str:
        """Generate vision statement"""
        
        industry = business_data.get("industry", "")
        
        visions = {
            "restaurant": "Ser reconhecido como o melhor restaurante da região, referência em qualidade e inovação gastronômica.",
            "healthcare": "Tornar-se um centro de excelência em saúde, reconhecido pela qualidade do atendimento e resultados positivos.",
            "ecommerce": "Ser a primeira escolha dos consumidores online, líder em satisfação e confiabilidade.",
            "services": "Ser referência no mercado, reconhecido pela excelência e inovação em nossos serviços.",
            "education": "Ser uma instituição de ensino modelo, formando os líderes e inovadores do amanhã."
        }
        
        return visions.get(industry, visions["services"])
    
    def _generate_values(self, business_data: Dict[str, Any]) -> List[str]:
        """Generate company values"""
        
        return [
            "Qualidade em tudo que fazemos",
            "Compromisso com nossos clientes",
            "Inovação constante",
            "Ética e transparência",
            "Responsabilidade social",
            "Trabalho em equipe"
        ]
    
    def _get_default_services(self, industry: str) -> List[str]:
        """Get default services by industry"""
        
        services = {
            "restaurant": [
                "Almoço Executivo",
                "Jantar Especial",
                "Delivery",
                "Eventos e Festas",
                "Catering",
                "Happy Hour"
            ],
            "healthcare": [
                "Consultas Médicas",
                "Exames Laboratoriais",
                "Check-up Completo",
                "Vacinação",
                "Atendimento de Urgência",
                "Telemedicina"
            ],
            "ecommerce": [
                "Venda Online",
                "Entrega Rápida",
                "Pagamento Seguro",
                "Atendimento ao Cliente",
                "Troca e Devolução",
                "Programa de Fidelidade"
            ],
            "services": [
                "Consultoria Especializada",
                "Análise e Diagnóstico",
                "Implementação de Soluções",
                "Suporte Técnico",
                "Treinamento",
                "Manutenção"
            ],
            "education": [
                "Cursos Presenciais",
                "Cursos Online",
                "Workshops",
                "Certificações",
                "Mentoria",
                "Material Didático"
            ]
        }
        
        return services.get(industry, services["services"])
    
    def _generate_service_description(self, service: str, industry: str) -> str:
        """Generate description for a service"""
        
        # Generic template
        return f"Oferecemos {service.lower()} com qualidade superior e atendimento personalizado para atender suas necessidades."
    
    def _get_service_icon(self, service: str) -> str:
        """Get icon for service"""
        
        # Map common service keywords to icons
        icon_map = {
            "delivery": "fas fa-truck",
            "consulta": "fas fa-stethoscope",
            "exame": "fas fa-microscope",
            "curso": "fas fa-graduation-cap",
            "suporte": "fas fa-headset",
            "pagamento": "fas fa-credit-card",
            "segurança": "fas fa-shield-alt",
            "atendimento": "fas fa-user-tie",
            "online": "fas fa-globe",
            "urgência": "fas fa-ambulance"
        }
        
        service_lower = service.lower()
        for keyword, icon in icon_map.items():
            if keyword in service_lower:
                return icon
        
        return "fas fa-check-circle"  # Default icon
    
    async def _call_ai(self, prompt: str) -> Dict[str, Any]:
        """Call AI provider (placeholder)"""
        
        # In production, integrate with actual AI provider
        # For now, return mock response
        return {
            "status": "success",
            "content": {}
        }
    
    async def optimize_content(
        self,
        content: str,
        optimization_type: str = "clarity"
    ) -> str:
        """
        Optimize existing content
        
        Args:
            content: Content to optimize
            optimization_type: Type of optimization (clarity, seo, engagement)
            
        Returns:
            Optimized content
        """
        
        if optimization_type == "clarity":
            # Simplify and clarify content
            return content
        elif optimization_type == "seo":
            # Add SEO keywords and structure
            return content
        elif optimization_type == "engagement":
            # Make content more engaging
            return content
        
        return content
    
    async def localize_content(
        self,
        content: Dict[str, Any],
        target_locale: str = "pt-BR"
    ) -> Dict[str, Any]:
        """
        Localize content for Brazilian market
        
        Args:
            content: Content to localize
            target_locale: Target locale
            
        Returns:
            Localized content
        """
        
        # Add Brazilian expressions and cultural references
        localized = content.copy()
        
        # Replace generic terms with Brazilian ones
        replacements = {
            "customer service": "atendimento ao cliente",
            "free shipping": "frete grátis",
            "discount": "desconto",
            "sale": "promoção",
            "contact us": "fale conosco",
            "about us": "sobre nós"
        }
        
        # Apply replacements
        for key, value in localized.items():
            if isinstance(value, str):
                for eng, ptbr in replacements.items():
                    value = value.replace(eng, ptbr)
                localized[key] = value
        
        return localized