import { PublicLayout } from '@/components/layouts/public-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'
import {
  Zap,
  Globe,
  Palette,
  BarChart3,
  Shield,
  Clock,
  Star,
  ArrowRight,
  Check,
} from 'lucide-react'

export default function HomePage() {
  return (
    <PublicLayout>
      {/* Hero Section */}
      <section className="py-20 px-4 text-center bg-gradient-to-br from-primary/5 via-background to-secondary/5">
        <div className="container mx-auto max-w-6xl">
          <div className="mx-auto max-w-3xl space-y-6">
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
              Crie Sites WordPress com <span className="text-primary">Inteligência Artificial</span>
            </h1>
            <p className="text-xl text-muted-foreground">
              Transforme suas ideias em sites profissionais em minutos. Nossa IA cria, otimiza e
              mantém seu WordPress automaticamente.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild>
                <Link href="/register">
                  <Zap className="mr-2 h-5 w-5" />
                  Começar Grátis
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/demo">
                  Ver Demo
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </div>
            <div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Check className="h-4 w-4 text-green-500" />
                Sem cartão de crédito
              </div>
              <div className="flex items-center gap-1">
                <Check className="h-4 w-4 text-green-500" />
                Setup em 3 minutos
              </div>
              <div className="flex items-center gap-1">
                <Check className="h-4 w-4 text-green-500" />
                Suporte 24/7
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Tudo que Você Precisa em Uma Plataforma</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Da criação à manutenção, nossa plataforma cuida de tudo para que você foque no que
              realmente importa: seu negócio.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Criação com IA</CardTitle>
                <CardDescription>
                  Descreva sua ideia e nossa IA cria um site completo em minutos, com design
                  profissional e conteúdo otimizado.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Globe className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>WordPress Nativo</CardTitle>
                <CardDescription>
                  Sites 100% WordPress, com todos os recursos e plugins que você conhece. Acesso
                  completo ao wp-admin.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Palette className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Design Inteligente</CardTitle>
                <CardDescription>
                  Templates modernos e responsivos, otimizados para conversão. Personalização
                  avançada via IA.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <BarChart3 className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Analytics Avançado</CardTitle>
                <CardDescription>
                  Dashboards completos com métricas de tráfego, conversões e performance. Relatórios
                  automáticos por email.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Segurança Total</CardTitle>
                <CardDescription>
                  Backups automáticos, SSL grátis, firewall avançado e monitoramento 24/7. Seus
                  sites sempre protegidos.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Clock className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Automação Completa</CardTitle>
                <CardDescription>
                  Updates automáticos, otimização de performance, geração de conteúdo e manutenção
                  sem você precisar se preocupar.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 bg-primary/5">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary mb-2">10.000+</div>
              <div className="text-muted-foreground">Sites Criados</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">99.9%</div>
              <div className="text-muted-foreground">Uptime Garantido</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">&lt;3min</div>
              <div className="text-muted-foreground">Tempo de Criação</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">24/7</div>
              <div className="text-muted-foreground">Suporte Premium</div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">O Que Nossos Clientes Dizem</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 text-yellow-500 fill-current" />
                  ))}
                </div>
                <p className="text-muted-foreground mb-4">
                  "Incrível! Criei 5 sites para meus clientes em uma tarde. A qualidade é
                  impressionante e o suporte é excepcional."
                </p>
                <div className="font-medium">Marina Silva</div>
                <div className="text-sm text-muted-foreground">Designer Freelancer</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 text-yellow-500 fill-current" />
                  ))}
                </div>
                <p className="text-muted-foreground mb-4">
                  "Automatizamos nossa agência com esta plataforma. Conseguimos entregar 3x mais
                  sites no mesmo tempo."
                </p>
                <div className="font-medium">Carlos Mendes</div>
                <div className="text-sm text-muted-foreground">CEO, WebStudio</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 text-yellow-500 fill-current" />
                  ))}
                </div>
                <p className="text-muted-foreground mb-4">
                  "Nunca imaginei que criar um site profissional pudesse ser tão fácil. Em 10
                  minutos minha loja estava no ar!"
                </p>
                <div className="font-medium">Ana Santos</div>
                <div className="text-sm text-muted-foreground">Empreendedora</div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-primary">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-3xl font-bold text-primary-foreground mb-4">
            Pronto para Revolucionar sua Criação de Sites?
          </h2>
          <p className="text-primary-foreground/80 text-lg mb-8">
            Junte-se a milhares de profissionais que já descobriram o poder da IA para WordPress.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" asChild>
              <Link href="/register">
                Começar Gratuitamente
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="text-primary-foreground border-primary-foreground hover:bg-primary-foreground hover:text-primary"
              asChild
            >
              <Link href="/contact">Falar com Consultor</Link>
            </Button>
          </div>
        </div>
      </section>
    </PublicLayout>
  )
}
