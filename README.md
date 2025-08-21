# 🚀 WordPress AI Builder

Plataforma SaaS para criação automatizada de sites WordPress com Inteligência Artificial.

## ✅ Fase 1 - FUNDAÇÃO COMPLETA

### 🎯 Status: Concluída
Todas as 12 tasks da Fase 1 foram implementadas com sucesso:

- ✅ **ESLint + Prettier + Husky** - Code quality e git hooks
- ✅ **Docker** - Ambiente de desenvolvimento containerizado
- ✅ **Variáveis de Ambiente** - Sistema de configuração seguro
- ✅ **Sistema de Logging** - Winston com rotação de arquivos
- ✅ **GitHub Actions CI/CD** - Pipeline automatizado
- ✅ **Testes** - Jest + Testing Library configurado
- ✅ **Design Tokens** - Sistema de design escalável
- ✅ **Componentes UI** - shadcn/ui base implementado
- ✅ **Sistema de Notificações** - Toast system completo
- ✅ **Layouts** - Dashboard e Public layouts prontos
- ✅ **Tema Dark/Light** - Sistema de temas funcional
- ✅ **Monitoramento** - Sentry para tracking de erros

## 🛠 Tech Stack

### Frontend
- **Next.js 15.1** - Framework React com App Router
- **TypeScript** - Type safety completo
- **Tailwind CSS 3.4** - Styling system
- **shadcn/ui** - Componentes base
- **Radix UI** - Componentes acessíveis
- **Framer Motion** - Animações
- **next-themes** - Sistema de temas

### Backend & Database
- **Prisma** - ORM e database toolkit
- **PostgreSQL** - Database principal
- **Redis** - Cache e filas

### DevOps & Tooling
- **Docker** - Containerização
- **GitHub Actions** - CI/CD
- **ESLint + Prettier** - Code formatting
- **Husky + lint-staged** - Git hooks
- **Jest** - Testing framework
- **Sentry** - Error monitoring
- **Winston** - Logging system

## 🚀 Como Executar

### 1. Ambiente Local (Recomendado)
```bash
# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local

# Executar em modo desenvolvimento
npm run dev
```

### 2. Docker (Opcional)
```bash
# Executar com Docker Compose
docker-compose up --build

# Acessar:
# - Aplicação: http://localhost:3000
# - Database Admin: http://localhost:8080
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

## 📁 Estrutura do Projeto

```
wordpress-ai-builder/
├── app/                    # Next.js App Router
│   ├── dashboard/         # Dashboard pages
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx          # Home page
├── components/            # React components
│   ├── layouts/          # Layout components
│   ├── ui/              # Base UI components
│   ├── theme-provider.tsx
│   └── theme-toggle.tsx
├── lib/                  # Utilities & configs
│   ├── cn.ts            # Class name utility
│   ├── design-tokens.ts  # Design system
│   ├── env.ts           # Environment validation
│   ├── logger.ts        # Logging system
│   └── use-toast.ts     # Toast hook
├── prisma/              # Database
│   └── schema.prisma    # Database schema
├── __tests__/           # Test files
├── .github/             # GitHub workflows
└── docker/              # Docker configs
```

## 🧪 Comandos Disponíveis

```bash
# Desenvolvimento
npm run dev              # Servidor de desenvolvimento
npm run build           # Build de produção
npm run start           # Servidor de produção

# Qualidade de código
npm run lint            # ESLint
npm run test            # Executar testes
npm run test:watch      # Testes em modo watch
npm run test:coverage   # Coverage report

# Database
npm run prisma:generate # Gerar Prisma client
npm run prisma:migrate  # Executar migrations
npm run prisma:studio   # Database GUI
```

## 🎨 Sistema de Design

O projeto utiliza um sistema de design tokens centralizado:

- **Cores**: Sistema semântico com support para dark/light
- **Tipografia**: Inter como fonte principal
- **Espaçamento**: Grid system responsivo
- **Componentes**: shadcn/ui como base
- **Animações**: Framer Motion integrado

## 🧩 Componentes Implementados

### UI Components
- `Button` - Com variants e loading states
- `Input` - Com validation styling
- `Card` - Layout component
- `Dialog` - Modal system
- `Toast` - Notification system

### Layout Components
- `DashboardLayout` - Sidebar navigation
- `PublicLayout` - Marketing site layout

## 📊 Próximas Fases

### Fase 2: Core Platform (3 semanas)
- Dashboard com métricas
- Gerenciamento de sites
- Integração WordPress básica

### Fase 3: AI Integration (3 semanas)
- Sistema de geração com IA
- Content automation
- Template engine

### Fase 4+: Features Avançadas
- Sistema de billing
- Landing page builder
- Site cloner
- Customer success tools

## 🔧 Configuração de Desenvolvimento

### Pré-requisitos
- Node.js 20+
- PostgreSQL
- Redis (opcional para desenvolvimento)

### Setup Inicial
1. Clone o repositório
2. Execute `npm install`
3. Configure `.env.local` com suas credenciais
4. Execute `npm run dev`

### Docker Setup (Alternativo)
1. Execute `docker-compose up --build`
2. Tudo estará configurado automaticamente

## 📚 Documentação

- [Roadmap Completo](./ROADMAP.md) - Todas as fases detalhadas
- [Design Tokens](./lib/design-tokens.ts) - Sistema de design
- [Environment Setup](./lib/env.ts) - Configuração de ambiente

## 🤝 Contribuição

Este projeto segue as melhores práticas:
- Commits seguem conventional commits
- PRs passam por CI/CD completo
- Code review obrigatório
- 80%+ test coverage

## 📄 Licença

Propriedade privada - WordPress AI Builder SaaS Platform

---

**🎉 Fase 1 Concluída com Sucesso!**

Base sólida estabelecida para desenvolvimento das próximas fases do WordPress AI Builder.