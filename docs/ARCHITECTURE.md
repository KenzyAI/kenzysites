# Arquitetura do Sistema KenzySites

## Visão Geral

O KenzySites é uma plataforma SaaS para criação e gestão de sites WordPress por assinatura, utilizando IA para personalização e templates ACF (Advanced Custom Fields) para máxima flexibilidade.

## Modelo de Arquitetura: Instalações Isoladas

### Por que Instalações Isoladas?

Após análise detalhada, optamos por **instalações WordPress isoladas** para cada cliente em vez de WordPress Multisite ou arquitetura multi-tenant. Esta decisão foi baseada em:

#### Vantagens das Instalações Isoladas

1. **Segurança Máxima**
   - Isolamento completo entre clientes
   - Sem risco de vazamento de dados entre sites
   - Cada site tem seu próprio banco de dados
   - Vulnerabilidade em um site não afeta outros

2. **Performance Dedicada**
   - Recursos computacionais dedicados por cliente
   - Sem competição por recursos entre sites
   - Otimização individual possível
   - Cache independente por instalação

3. **Flexibilidade Total**
   - Qualquer plugin pode ser instalado
   - Temas customizados sem restrições
   - Versões diferentes do WordPress se necessário
   - Configurações PHP personalizadas

4. **Backup e Restore Independente**
   - Backups individuais por site
   - Restore sem afetar outros clientes
   - Migração simplificada
   - Disaster recovery granular

5. **Escalabilidade Horizontal**
   - Fácil distribuição em múltiplos servidores
   - Load balancing por cliente
   - Scaling automático baseado em demanda

### Arquitetura Técnica

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│                   Dashboard de Gerenciamento                 │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend API (FastAPI)                    │
│               Orquestração e Gestão de Sites                 │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   Kubernetes     │ │   Agno Framework │ │   ACF Service    │
│   Orchestrator   │ │   (AI Agents)    │ │   (Templates)    │
└──────────────────┘ └──────────────────┘ └──────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                    WordPress Containers                      │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Site Cliente 1 │  Site Cliente 2 │     Site Cliente N      │
│  ┌───────────┐  │  ┌───────────┐  │     ┌───────────┐      │
│  │ WordPress │  │  │ WordPress │  │     │ WordPress │      │
│  │    +      │  │  │    +      │  │     │    +      │      │
│  │   MySQL   │  │  │   MySQL   │  │     │   MySQL   │      │
│  │    +      │  │  │    +      │  │     │    +      │      │
│  │   Redis   │  │  │   Redis   │  │     │   Redis   │      │
│  └───────────┘  │  └───────────┘  │     └───────────┘      │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Componentes da Arquitetura

#### 1. Container WordPress Isolado

Cada cliente recebe:
- **WordPress**: Instalação completa e independente
- **MySQL**: Banco de dados dedicado
- **Redis**: Cache dedicado
- **Nginx**: Servidor web otimizado
- **PHP-FPM**: Pool de processos PHP dedicado

```yaml
# Exemplo de configuração do container
version: '3.8'
services:
  wordpress_cliente_123:
    image: wordpress:latest-php8.2-fpm
    container_name: wp_cliente_123
    environment:
      WORDPRESS_DB_HOST: mysql_cliente_123
      WORDPRESS_DB_USER: wp_user_123
      WORDPRESS_DB_PASSWORD: ${SECURE_PASSWORD}
      WORDPRESS_DB_NAME: wp_db_123
    volumes:
      - ./sites/cliente_123/wp-content:/var/www/html/wp-content
      - ./sites/cliente_123/uploads:/var/www/html/wp-content/uploads
    networks:
      - isolated_network_123
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

#### 2. Integração ACF (Advanced Custom Fields)

Cada template usa ACF para máxima flexibilidade:

```python
# Estrutura ACF por tipo de negócio
ACF_TEMPLATES = {
    "restaurante": {
        "fields": ["menu", "horarios", "delivery", "reservas"],
        "repeaters": ["pratos", "categorias_menu"],
        "options": ["WhatsApp", "PIX", "iFood"]
    },
    "advocacia": {
        "fields": ["areas_atuacao", "oab", "consultas"],
        "repeaters": ["casos_sucesso", "equipe"],
        "options": ["agendamento", "LGPD"]
    },
    "saude": {
        "fields": ["especialidades", "convenios", "crm"],
        "repeaters": ["medicos", "procedimentos"],
        "options": ["telemedicina", "agendamento"]
    }
}
```

#### 3. Sistema de Provisionamento

Fluxo de criação de novo site:

1. **Requisição de Novo Site**
   ```python
   POST /api/sites/generate
   {
     "business_name": "Restaurante do João",
     "industry": "restaurante",
     "template": "restaurant_modern"
   }
   ```

2. **Orquestração via Kubernetes**
   ```bash
   # Criar namespace isolado
   kubectl create namespace cliente-123
   
   # Deploy do WordPress
   kubectl apply -f wordpress-deployment.yaml -n cliente-123
   
   # Configurar ACF
   wp plugin install advanced-custom-fields-pro --activate
   wp acf import --json_file=restaurant_fields.json
   ```

3. **Personalização com IA**
   - Agno Framework gera conteúdo personalizado
   - ACF fields são preenchidos automaticamente
   - Imagens são geradas ou selecionadas

4. **Ativação e DNS**
   - Subdomínio é configurado
   - SSL é provisionado (Let's Encrypt)
   - CDN é ativado (Cloudflare)

### Segurança e Isolamento

#### Níveis de Isolamento

1. **Network Isolation**
   - Cada site tem sua própria rede virtual
   - Comunicação entre sites é bloqueada
   - Firewall rules específicas por cliente

2. **Resource Isolation**
   - CPU e memória limitados por container
   - I/O throttling para evitar abuse
   - Quotas de disco por cliente

3. **Data Isolation**
   - Bancos de dados separados
   - Backups independentes
   - Encryption at rest

#### Segurança Implementada

```python
# Configurações de segurança por site
SECURITY_CONFIG = {
    "wordpress": {
        "disable_file_edit": True,
        "force_ssl": True,
        "limit_login_attempts": True,
        "two_factor_auth": "optional",
        "security_headers": {
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block"
        }
    },
    "firewall": {
        "block_xmlrpc": True,
        "block_author_scans": True,
        "rate_limiting": "100/minute",
        "geo_blocking": "optional"
    },
    "monitoring": {
        "file_integrity": True,
        "malware_scan": "daily",
        "uptime_monitoring": True,
        "performance_monitoring": True
    }
}
```

### Escalabilidade

#### Estratégia de Scaling

1. **Vertical Scaling**
   - Upgrade de recursos do container
   - Mais CPU/RAM conforme necessário
   - Automático baseado em métricas

2. **Horizontal Scaling**
   - Múltiplos nodes Kubernetes
   - Distribuição geográfica
   - Load balancing inteligente

3. **Auto-scaling Rules**
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: wordpress-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: wordpress
     minReplicas: 1
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
     - type: Resource
       resource:
         name: memory
         target:
           type: Utilization
           averageUtilization: 80
   ```

### Monitoramento e Observabilidade

#### Stack de Monitoramento

- **Prometheus**: Métricas de sistema
- **Grafana**: Dashboards e visualização
- **Loki**: Agregação de logs
- **Jaeger**: Distributed tracing
- **Uptime Kuma**: Monitoramento de disponibilidade

#### Métricas Monitoradas

```python
MONITORING_METRICS = {
    "performance": [
        "page_load_time",
        "time_to_first_byte",
        "database_query_time",
        "cache_hit_ratio"
    ],
    "availability": [
        "uptime_percentage",
        "error_rate",
        "response_codes"
    ],
    "resources": [
        "cpu_usage",
        "memory_usage",
        "disk_usage",
        "network_throughput"
    ],
    "business": [
        "active_sites",
        "api_calls",
        "ai_credits_used",
        "storage_consumed"
    ]
}
```

### Backup e Disaster Recovery

#### Estratégia de Backup

1. **Backups Automáticos**
   - Diários: Últimos 30 dias
   - Semanais: Últimas 8 semanas
   - Mensais: Últimos 12 meses

2. **Tipos de Backup**
   - Full backup: WordPress files + Database
   - Incremental: Apenas mudanças
   - Snapshot: Estado completo do container

3. **Armazenamento**
   ```python
   BACKUP_STORAGE = {
       "primary": "S3 (ou Cloudflare R2)",
       "secondary": "Google Cloud Storage",
       "retention": {
           "daily": 30,
           "weekly": 8,
           "monthly": 12
       },
       "encryption": "AES-256",
       "compression": "gzip"
   }
   ```

#### Recovery Process

1. **Point-in-Time Recovery**
   - Restore para qualquer ponto nos últimos 30 dias
   - RPO (Recovery Point Objective): 1 hora
   - RTO (Recovery Time Objective): 15 minutos

2. **Disaster Recovery Plan**
   - Multi-region replication
   - Automated failover
   - Regular DR drills

### Custos e Otimização

#### Estrutura de Custos por Site

```python
COST_STRUCTURE = {
    "infrastructure": {
        "compute": "R$ 5-15/mês",  # Por container
        "storage": "R$ 0.10/GB",
        "bandwidth": "R$ 0.05/GB",
        "backup": "R$ 0.02/GB"
    },
    "services": {
        "monitoring": "R$ 2/site",
        "ssl": "Free (Let's Encrypt)",
        "cdn": "R$ 5/site (Cloudflare)"
    },
    "total_per_site": "R$ 15-30/mês"
}
```

#### Otimizações Implementadas

1. **Resource Pooling**
   - Compartilhamento de recursos não utilizados
   - Scaling down automático em horários de baixo uso

2. **Caching Strategy**
   - Redis para cache de objetos
   - Cloudflare para cache de edge
   - Browser caching otimizado

3. **Image Optimization**
   - Conversão automática para WebP
   - Lazy loading
   - Responsive images

### Comparação com Outras Arquiteturas

| Aspecto | Instalações Isoladas | WordPress Multisite | Multi-tenant Custom |
|---------|---------------------|---------------------|-------------------|
| **Segurança** | ⭐⭐⭐⭐⭐ Máxima | ⭐⭐⭐ Média | ⭐⭐⭐⭐ Alta |
| **Performance** | ⭐⭐⭐⭐⭐ Dedicada | ⭐⭐⭐ Compartilhada | ⭐⭐⭐⭐ Boa |
| **Flexibilidade** | ⭐⭐⭐⭐⭐ Total | ⭐⭐ Limitada | ⭐⭐⭐ Média |
| **Custo Infra** | ⭐⭐⭐ Médio-Alto | ⭐⭐⭐⭐⭐ Baixo | ⭐⭐⭐⭐ Médio |
| **Complexidade** | ⭐⭐⭐ Média | ⭐⭐⭐⭐⭐ Baixa | ⭐⭐ Alta |
| **Manutenção** | ⭐⭐⭐ Individual | ⭐⭐⭐⭐⭐ Centralizada | ⭐⭐⭐⭐ Centralizada |
| **Escalabilidade** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐ Limitada | ⭐⭐⭐⭐ Boa |
| **Backup/Restore** | ⭐⭐⭐⭐⭐ Granular | ⭐⭐ Complexo | ⭐⭐⭐ Médio |

### Conclusão

A arquitetura de **instalações WordPress isoladas** oferece o melhor equilíbrio entre:
- Segurança e isolamento total
- Flexibilidade para customização
- Performance dedicada
- Facilidade de manutenção
- Escalabilidade horizontal

Com a integração de ACF e personalização via IA, conseguimos oferecer sites únicos e personalizados mantendo a eficiência operacional através da automação completa do provisionamento e gestão.

### Roadmap de Melhorias

1. **Curto Prazo (3 meses)**
   - Implementar edge caching global
   - Adicionar mais templates brasileiros
   - Melhorar automação de backups

2. **Médio Prazo (6 meses)**
   - Multi-region deployment
   - A/B testing automático
   - Analytics avançado integrado

3. **Longo Prazo (12 meses)**
   - Kubernetes federation para global scale
   - ML para otimização automática de performance
   - Marketplace de plugins/templates