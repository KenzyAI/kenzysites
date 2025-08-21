# E2E Tests com Playwright

Este diretório contém todos os testes end-to-end (E2E) para o WordPress AI Builder, implementados usando Playwright.

## 📁 Estrutura

```
e2e/
├── tests/           # Arquivos de teste
│   ├── homepage.spec.ts        # Testes da página inicial
│   ├── auth.spec.ts           # Testes de autenticação
│   ├── site-creation.spec.ts  # Testes de criação de sites
│   ├── dashboard.spec.ts      # Testes do dashboard
│   ├── responsive.spec.ts     # Testes de responsividade
│   ├── accessibility.spec.ts  # Testes de acessibilidade
│   └── visual.spec.ts         # Testes de regressão visual
├── fixtures/        # Fixtures customizadas
│   └── test-base.ts          # Base para todos os testes
├── utils/          # Utilitários e helpers
│   └── helpers.ts            # Funções auxiliares
└── data/           # Dados de teste
    └── test-data.ts          # Dados mockados e constantes
```

## 🚀 Como Executar

### Comandos Básicos

```bash
# Executar todos os testes E2E
npm run test:e2e

# Executar com interface visual
npm run test:e2e:ui

# Executar em modo headed (visualizando o browser)
npm run test:e2e:headed

# Executar em modo debug
npm run test:e2e:debug

# Executar testes específicos
npx playwright test homepage.spec.ts

# Executar apenas em um browser
npx playwright test --project=chromium
```

### Executar com Diferentes Ambientes

```bash
# Ambiente local (padrão)
npm run test:e2e

# Ambiente de staging
PLAYWRIGHT_BASE_URL=https://staging.example.com npm run test:e2e

# Ambiente de produção
PLAYWRIGHT_BASE_URL=https://production.example.com npm run test:e2e
```

## 🧪 Tipos de Testes

### 1. Testes Funcionais
- **Homepage** (`homepage.spec.ts`): Verifica conteúdo, navegação e CTAs
- **Autenticação** (`auth.spec.ts`): Login, registro, logout e recuperação de senha
- **Criação de Sites** (`site-creation.spec.ts`): Fluxo completo de criação com IA
- **Dashboard** (`dashboard.spec.ts`): Gestão de sites e funcionalidades do painel

### 2. Testes de Responsividade
- **Responsive** (`responsive.spec.ts`): Testa layouts em diferentes dispositivos
  - Mobile (375x667)
  - Tablet (768x1024)
  - Desktop (1280x720)
  - Large Desktop (1920x1080)

### 3. Testes de Acessibilidade
- **Accessibility** (`accessibility.spec.ts`): Conformidade com WCAG 2.1
  - Navegação por teclado
  - Leitores de tela
  - Contraste de cores
  - Semântica HTML

### 4. Testes Visuais
- **Visual** (`visual.spec.ts`): Regressão visual e consistência de design
  - Screenshots de componentes
  - Comparação entre temas (claro/escuro)
  - Estados de hover e foco

## 🛠️ Configuração

### Ambiente de Desenvolvimento

1. **Instalar dependências:**
```bash
npm install
```

2. **Instalar browsers do Playwright:**
```bash
npx playwright install
```

3. **Configurar variáveis de ambiente:**
```bash
cp .env.example .env.local
# Editar .env.local com suas configurações
```

### Configuração do Playwright

O arquivo `playwright.config.ts` na raiz do projeto contém:

- **Browsers**: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari
- **Base URL**: `http://localhost:3000` (configurável)
- **Timeouts**: 30s para testes, 120s para web server
- **Artifacts**: Screenshots, vídeos e traces em falhas
- **Reporters**: HTML, JUnit e lista

## 📊 Relatórios

### Visualizar Relatórios HTML

```bash
# Após executar os testes, abrir relatório
npx playwright show-report
```

### Artifacts Gerados

- **Screenshots**: Capturados em falhas
- **Vídeos**: Gravados em falhas e retries
- **Traces**: Para debug detalhado
- **Test Results**: Resultados em formato JUnit

## 🔧 Debugging

### Mode Debug Interativo

```bash
# Debug passo a passo
npm run test:e2e:debug

# Debug teste específico
npx playwright test homepage.spec.ts --debug
```

### Trace Viewer

```bash
# Visualizar traces de execução
npx playwright show-trace trace.zip
```

### Codegen - Gravação de Testes

```bash
# Gravar novos testes automaticamente
npx playwright codegen localhost:3000
```

## 📝 Escrevendo Novos Testes

### Estrutura Básica

```typescript
import { test, expect } from '../fixtures/test-base'
import { waitForNetworkIdle } from '../utils/helpers'

test.describe('Minha Funcionalidade', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/my-page')
    await waitForNetworkIdle(page)
    
    // Seu teste aqui
    await expect(page.locator('h1')).toBeVisible()
  })
})
```

### Boas Práticas

1. **Use data-testid** para elementos dinâmicos:
```html
<button data-testid="submit-button">Submit</button>
```

2. **Aguarde o carregamento** antes de interagir:
```typescript
await waitForNetworkIdle(page)
```

3. **Use fixtures customizadas** para setup comum:
```typescript
test('test with user', async ({ page, testUser }) => {
  // testUser já está disponível
})
```

4. **Mock APIs** quando necessário:
```typescript
await mockApiResponse(page, '**/api/users', { users: [] })
```

## 🚥 CI/CD

Os testes E2E são executados automaticamente no GitHub Actions:

- **Trigger**: Push e Pull Requests para `main` e `develop`
- **Browsers**: Todos os browsers configurados
- **Artifacts**: Relatórios e screenshots são salvos por 30 dias
- **Parallelização**: Testes executam em paralelo para velocidade

### Configuração no CI

```yaml
- name: Run Playwright tests
  run: npx playwright test
  env:
    PLAYWRIGHT_BASE_URL: http://localhost:3000
```

## 🔍 Monitoramento

### Métricas Importantes

- **Taxa de Sucesso**: > 95%
- **Tempo de Execução**: < 10 minutos
- **Cobertura de Fluxos**: Todos os críticos testados

### Alertas

- Falhas são reportadas no Slack/Email
- Screenshots anexados automaticamente
- Links para traces e relatórios detalhados

## 📚 Recursos Adicionais

- [Documentação Playwright](https://playwright.dev/)
- [Guia de Boas Práticas](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-page)
- [Seletores CSS](https://playwright.dev/docs/selectors)