# PRD - WordPress AI Site Builder SaaS Platform
*Product Requirements Document v1.0 - Agosto 2025*

## 1. Executive Summary

### 1.1 Visão do Produto
Plataforma SaaS completa para criação, gestão e manutenção automatizada de sites WordPress através de IA, oferecendo geração instantânea de sites, landing pages dinâmicas, clonagem de sites existentes e geração automática de conteúdo por assinatura.

### 1.2 Proposta de Valor Única (UVP)
- **Para Agências**: Redução de 95% no tempo de entrega de sites
- **Para Freelancers**: Capacidade de gerenciar 10x mais clientes
- **Para PMEs**: Sites profissionais mantidos automaticamente por 1/3 do custo tradicional
- **Diferencial**: Única plataforma que combina WordPress + Landing Pages + Clone + IA Content em modelo SaaS

### 1.3 Métricas de Sucesso
- **MRR Target**: R$ 50.000 em 6 meses, R$ 200.000 em 12 meses
- **Clientes Ativos**: 200 em 6 meses, 800 em 12 meses
- **Churn Rate**: < 5% mensal
- **CAC**: < R$ 150
- **LTV**: > R$ 3.500
- **NPS**: > 70

## 2. Contexto de Mercado

### 2.1 Análise de Mercado
- **TAM Brasil**: R$ 2.8 bilhões (mercado de desenvolvimento web)
- **SAM**: R$ 450 milhões (PMEs que precisam de sites)
- **SOM**: R$ 45 milhões (5% do SAM em 3 anos)

### 2.2 Competitors Analysis
| Concorrente | Preço | Pontos Fortes | Pontos Fracos | Nossa Vantagem |
|-------------|-------|---------------|---------------|----------------|
| ZipWP | $39/ano | WordPress nativo | Só em inglês | Localização BR + preço em BRL |
| Hostinger AI | $2.99/mês | Infraestrutura | Limitado | WordPress completo |
| 10Web.io | $20/mês | IA avançada | Caro | 3x mais barato |
| Wix ADI | R$ 29/mês | Fácil uso | Não é WordPress | WordPress = 43% web |

### 2.3 Personas Alvo

#### Persona 1: Marina - Freelancer Designer
- **Idade**: 28 anos
- **Dor**: Demora muito para entregar sites
- **Necessidade**: Criar sites rápidos mantendo qualidade
- **Budget**: R$ 200-500/mês

#### Persona 2: Carlos - Dono de Agência
- **Idade**: 35 anos
- **Dor**: Equipe cara e processos lentos
- **Necessidade**: Escalar entregas sem aumentar equipe
- **Budget**: R$ 1.000-3.000/mês

#### Persona 3: Ana - Empresária PME
- **Idade**: 42 anos
- **Dor**: Site desatualizado e caro para manter
- **Necessidade**: Site profissional com conteúdo atualizado
- **Budget**: R$ 100-300/mês

## 3. Requisitos Funcionais

### 3.1 Core Features (MVP)

#### F001: Geração de Sites WordPress com IA
- **Descrição**: Criar site WordPress completo via prompt
- **Acceptance Criteria**:
  - Gerar site em < 5 minutos
  - Mínimo 5 páginas (Home, Sobre, Serviços, Blog, Contato)
  - SEO otimizado automaticamente
  - Mobile responsive
  - Score PageSpeed > 90

#### F002: Dashboard de Gestão de Clientes
- **Descrição**: Interface para gerenciar todos os sites/clientes
- **Features**:
  - Lista de sites com status
  - Métricas de uso (visitantes, posts, etc)
  - Gestão de planos e pagamentos
  - Acesso rápido ao WP-Admin
  - Logs de atividades

#### F003: Sistema de Billing Recorrente
- **Descrição**: Cobrança automática mensal
- **Integrações**:
  - Asaas (Brasil) - Pix, Boleto, Cartão
  - Stripe (Internacional) - Cards, Wallets
- **Features**:
  - Retry automático
  - Dunning emails
  - Upgrade/downgrade de plano
  - Cupons de desconto

#### F004: Sistema de Suspensão Automática
- **Descrição**: Suspender sites por inadimplência
- **Workflow**:
  - D+3: Email de aviso
  - D+7: Site suspenso com paywall
  - D+15: Segundo aviso
  - D+30: Backup e exclusão agendada

### 3.2 Advanced Features (v2.0)

#### F005: Landing Page Builder (Bolt.DIY)
- **Descrição**: Criar landing pages sem WordPress
- **Features**:
  - Drag & drop visual
  - 500+ templates
  - A/B testing
  - Analytics integrado
  - Custom domains

#### F006: Site Cloner (Firecrawl)
- **Descrição**: Clonar qualquer site para WordPress
- **Process**:
  1. Crawl completo do site
  2. Análise de estrutura com IA
  3. Recriação em WordPress
  4. Otimização automática
- **Limitações**: Respeitar copyright

#### F007: Content Automation Engine
- **Descrição**: Gerar posts automaticamente
- **Features**:
  - Calendário editorial com IA
  - Pesquisa de keywords
  - Geração de imagens
  - Publicação agendada
  - Otimização SEO

#### F008: Colaboração em Tempo Real (Dyad)
- **Descrição**: Edição colaborativa de sites
- **Features**:
  - Multiplayer editing
  - Comentários inline
  - Versionamento
  - Preview compartilhado

### 3.3 Enterprise Features (v3.0)

#### F009: White Label
- **Descrição**: Agências com marca própria
- **Customização**:
  - Logo e cores
  - Domínio personalizado
  - Email templates
  - Preços customizados

#### F010: API Pública
- **Descrição**: Integração com sistemas externos
- **Endpoints**:
  - Create site
  - Manage content
  - Analytics data
  - Billing info
- **Rate Limits**: Por tier de plano

## 4. Requisitos Não-Funcionais

### 4.1 Performance
- **Site Generation**: < 5 minutos (p99)
- **API Response**: < 200ms (p95)
- **Dashboard Load**: < 2 segundos
- **Uptime**: 99.9% SLA
- **Concurrent Users**: 10,000+

### 4.2 Segurança
- **Compliance**: LGPD, GDPR
- **Encryption**: TLS 1.3, AES-256
- **Auth**: OAuth 2.0, MFA opcional
- **Isolation**: Container por cliente
- **Backups**: Daily, 30 dias retention
- **WAF**: Cloudflare Enterprise

### 4.3 Escalabilidade
- **Arquitetura**: Microserviços
- **Auto-scaling**: Horizontal
- **Database**: Sharding ready
- **Cache**: Multi-layer
- **CDN**: Global distribution

### 4.4 Usabilidade
- **Onboarding**: < 3 minutos
- **Learning Curve**: < 30 minutos
- **Acessibilidade**: WCAG AA
- **Mobile**: Responsive admin
- **Idiomas**: PT-BR, EN, ES

## 5. Arquitetura Técnica

### 5.1 Tech Stack Recomendada

#### Frontend
```yaml
Framework: Next.js 15.1 (App Router)
UI Library: shadcn/ui + Radix UI
Styling: Tailwind CSS v4 + CSS Modules
State: Zustand + TanStack Query v5
Forms: React Hook Form + Zod
Charts: Tremor v3 + Recharts
Animation: Framer Motion v12
Auth: Clerk / Auth.js v5
```

#### Backend
```yaml
API: FastAPI 0.115 (Python 3.12)
ORM: Prisma Python / SQLAlchemy 2.0
Queue: Celery + Redis / BullMQ
Cache: Redis + Cloudflare Cache
Search: Meilisearch / Typesense
Storage: S3 (Cloudflare R2)
```

#### AI/ML Stack
```yaml
Orchestration: Agno Framework
Primary LLM: Claude 3.5 Sonnet
Secondary: GPT-4o, Gemini 2.0
Embeddings: text-embedding-3-large
Vector DB: Pinecone / Qdrant
Image Gen: DALL-E 3, SDXL
```

#### WordPress Management
```yaml
Architecture: Isolated Instances
Container: Docker + K8s
Management: WP-CLI + REST API
Themes: Astra, GeneratePress
Builders: Gutenberg, Elementor
Cache: LiteSpeed, Redis
```

#### Infrastructure
```yaml
Orchestration: Kubernetes (K3s)
Registry: Harbor / DockerHub
CI/CD: GitHub Actions + ArgoCD
Monitoring: Grafana + Prometheus
APM: Datadog / New Relic
Logs: Loki + Promtail
```

### 5.2 Integrations

#### Payment Gateways
- **Asaas**: PIX, Boleto, Cartão (Brasil)
- **Stripe**: Cards, Wallets (Internacional)
- **PayPal**: Opcional para US/EU

#### Communication
- **Email**: SendGrid / Resend
- **SMS**: Twilio / Vonage
- **Push**: OneSignal
- **Chat**: Intercom / Crisp

#### Analytics
- **Product**: Mixpanel / PostHog
- **Web**: Plausible / Umami
- **Error**: Sentry
- **Performance**: SpeedCurve

## 6. Planos e Preços

### 6.1 Estrutura de Planos

| Feature | Starter | Professional | Business | Agency |
|---------|---------|--------------|----------|---------|
| **Preço Brasil** | R$ 97/mês | R$ 297/mês | R$ 597/mês | R$ 1.997/mês |
| **Preço Global** | $19/mês | $59/mês | $119/mês | $399/mês |
| **Sites WordPress** | 1 | 5 | 15 | Ilimitado |
| **Landing Pages** | 3 | 15 | 50 | Ilimitado |
| **AI Credits/mês** | 1.000 | 5.000 | 15.000 | 50.000 |
| **Blog Posts/mês** | 4 | 20 | 60 | 200 |
| **Clonagem/mês** | - | 2 | 10 | Ilimitado |
| **Armazenamento** | 10GB | 50GB | 200GB | 1TB |
| **Bandwidth** | 100GB | 500GB | 2TB | Ilimitado |
| **Suporte** | Email | Priority | Phone | Dedicado |
| **White Label** | - | - | - | ✅ |
| **API Access** | - | Básico | Completo | Completo |
| **Usuários** | 1 | 3 | 10 | Ilimitado |

### 6.2 AI Credits System

| Ação | Credits |
|------|---------|
| Gerar site completo | 100 |
| Criar landing page | 50 |
| Clonar site | 150 |
| Gerar blog post | 20 |
| Gerar imagem | 5 |
| Redesign página | 30 |
| SEO optimization | 10 |

## 7. Roadmap de Desenvolvimento

### 7.1 Phase 1: MVP (Mês 1-2)
**Goal**: Validar conceito core

**Entregáveis**:
- [x] Gerador WordPress com IA básico
- [x] Dashboard administrativo
- [x] Sistema de billing (Asaas)
- [x] 3 templates base
- [x] Deploy automatizado
- [x] 10 clientes beta

**Tech Debt Aceitável**:
- UI básica
- Apenas português
- Suporte manual

### 7.2 Phase 2: Beta Público (Mês 3-4)
**Goal**: Refinar produto com feedback

**Entregáveis**:
- [x] Landing page builder (Bolt.DIY)
- [x] Content automation básico
- [x] Customer portal
- [x] 10 templates adicionais
- [x] Onboarding automatizado
- [x] 50 clientes beta

**Melhorias**:
- UI polida
- Performance otimizada
- Documentação

### 7.3 Phase 3: Launch Oficial (Mês 5-6)
**Goal**: Go-to-market agressivo

**Entregáveis**:
- [x] Site cloner (Firecrawl)
- [x] Stripe internacional
- [x] White label básico
- [x] Marketing automation
- [x] Affiliate program
- [x] 200 clientes pagantes

**Marketing**:
- Product Hunt launch
- Lifetime deals
- Influencer partnerships

### 7.4 Phase 4: Scale (Mês 7-12)
**Goal**: Crescimento e expansão

**Entregáveis**:
- [x] Dyad collaboration
- [x] Mobile app (React Native)
- [x] API marketplace
- [x] Enterprise features
- [x] Multi-idioma (EN, ES)
- [x] 800+ clientes

**Expansão**:
- Parcerias B2B
- Revendedores
- Internacional

### 7.5 Phase 5: Platform (Ano 2)
**Goal**: Ecossistema completo

**Visão**:
- Marketplace de templates
- SDK para desenvolvedores
- Certificação para agências
- AI training customizado
- Aquisições estratégicas

## 8. Equipe e Recursos

### 8.1 Equipe Mínima (MVP)

| Papel | Quantidade | Responsabilidade |
|-------|------------|------------------|
| Product Manager | 1 | Visão e roadmap |
| Full-Stack Dev | 2 | Core platform |
| AI/ML Engineer | 1 | Integrações IA |
| DevOps | 1 | Infra e deploy |
| UI/UX Designer | 1 | Interface e UX |
| Customer Success | 1 | Suporte e onboarding |

### 8.2 Equipe Ideal (Scale)

| Área | Headcount | Foco |
|------|-----------|------|
| Produto | 3 | PM, PO, UX Researcher |
| Engenharia | 8 | Backend, Frontend, AI, DevOps |
| Design | 2 | Product, Marketing |
| Marketing | 3 | Growth, Content, Paid |
| Vendas | 2 | Inside Sales, Partnerships |
| Customer Success | 3 | Support, Success, Docs |
| Operations | 1 | Finance, Legal, HR |

### 8.3 Budget Estimado

#### Custos Mensais (MVP)
- **Equipe**: R$ 60.000
- **Infraestrutura**: R$ 5.000
- **APIs (OpenAI, etc)**: R$ 3.000
- **Tools/Software**: R$ 2.000
- **Marketing**: R$ 5.000
- **Total**: R$ 75.000

#### Unit Economics (Target)
- **CAC**: R$ 150
- **LTV**: R$ 3.500
- **Payback**: 2 meses
- **Gross Margin**: 75%
- **Churn**: 5% mensal

## 9. Riscos e Mitigações

### 9.1 Riscos Técnicos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Custos IA explosivos | Alta | Alto | Cache agressivo, rate limits, modelos open-source |
| Complexidade WordPress | Média | Alto | Começar simples, parceria com devs WP |
| Segurança/Hacks | Média | Crítico | Isolamento, WAF, auditorias regulares |
| Performance ruim | Baixa | Alto | CDN, otimização, monitoring proativo |
| Vendor lock-in | Média | Médio | Abstrações, multi-provider strategy |

### 9.2 Riscos de Negócio

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Competição agressiva | Alta | Alto | Foco em nicho BR, diferenciação |
| Churn alto | Média | Alto | Onboarding excellence, customer success |
| Regulação IA | Baixa | Médio | Compliance proativo, termos claros |
| Crise econômica | Média | Alto | Plano freemium, pricing flexível |
| Dependência de poucos clientes | Alta | Médio | Diversificação, growth constante |

## 10. Métricas e KPIs

### 10.1 North Star Metrics
- **Primary**: Monthly Recurring Revenue (MRR)
- **Secondary**: Active Sites Generated
- **Tertiary**: Customer Satisfaction (NPS)

### 10.2 Métricas por Área

#### Produto
- Feature Adoption Rate
- Time to Value (TTV)
- User Engagement Score
- AI Accuracy Rate

#### Engenharia
- Deploy Frequency
- Lead Time for Changes
- MTTR (Mean Time to Recovery)
- Change Failure Rate

#### Marketing
- CAC by Channel
- Conversion Rate
- Organic Traffic Growth
- Content Engagement

#### Customer Success
- Churn Rate
- Expansion Revenue
- Support Ticket Resolution
- Onboarding Completion

#### Financeiro
- Burn Rate
- Runway
- Gross Margin
- Cash Flow

## 11. Definição de Sucesso

### 11.1 Critérios de Sucesso (Ano 1)
- ✅ 800+ clientes ativos
- ✅ R$ 200k+ MRR
- ✅ Churn < 5%
- ✅ NPS > 70
- ✅ Break-even operacional

### 11.2 Visão de Longo Prazo (3 anos)
- Líder em WordPress AI no Brasil
- 10,000+ clientes ativos
- R$ 2M+ MRR
- Expansão LATAM
- Exit ou Series A

## 12. Apêndices

### A. Glossário Técnico
- **MRR**: Monthly Recurring Revenue
- **CAC**: Customer Acquisition Cost
- **LTV**: Lifetime Value
- **SaaS**: Software as a Service
- **API**: Application Programming Interface
- **K8s**: Kubernetes
- **WP**: WordPress

### B. Referências
- WordPress REST API Docs
- Agno Framework Documentation
- Bolt.DIY Integration Guide
- Firecrawl API Reference
- Stripe/Asaas Documentation

### C. Mockups e Wireframes
- [Link para Figma]
- [Link para Protótipo]
- [Link para User Journey]

### D. Análise de Viabilidade Técnica
- Todos os componentes validados
- POCs criados para integrações críticas
- Arquitetura escalável confirmada

---

*Documento criado em Agosto 2025*
*Versão: 1.0*
*Status: Em Revisão*
*Próxima Atualização: Setembro 2025*