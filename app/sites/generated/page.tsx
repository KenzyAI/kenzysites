'use client';

import { useState, useEffect, ReactElement } from 'react';
import { useRouter } from 'next/navigation';
import { 
  FileText, 
  Eye, 
  Download, 
  Settings, 
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Globe,
  Zap,
  Search,
  Filter,
  MoreVertical,
  Trash2,
  Edit,
  Copy,
  ExternalLink,
  Palette,
  Layers,
  Code
} from 'lucide-react';

interface GeneratedSite {
  id: string;
  personalization_id: string;
  business_name: string;
  industry: string;
  template_id: string;
  template_name: string;
  status: 'completed' | 'processing' | 'failed' | 'draft';
  created_at: string;
  generation_time: number;
  variations_count: number;
  selected_variation?: number;
  preview_url?: string;
  wordpress_url?: string;
  ai_credits_used: number;
  features: string[];
}

interface SiteStats {
  total_sites: number;
  sites_this_month: number;
  total_ai_credits: number;
  average_generation_time: number;
}

export default function GeneratedSitesDashboard() {
  const router = useRouter();
  const [sites, setSites] = useState<GeneratedSite[]>([]);
  const [stats, setStats] = useState<SiteStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterIndustry, setFilterIndustry] = useState<string>('all');
  const [selectedSite, setSelectedSite] = useState<string | null>(null);

  useEffect(() => {
    fetchSites();
    fetchStats();
  }, []);

  const fetchSites = async () => {
    try {
      // In production, fetch from API
      // const response = await fetch('http://localhost:8000/api/v2/generation/sites');
      // const data = await response.json();
      
      // Mock data for development
      const mockSites: GeneratedSite[] = [
        {
          id: 'gen_001',
          personalization_id: 'pers_001',
          business_name: 'Restaurante Sabor Brasileiro',
          industry: 'restaurant',
          template_id: 'tpl_restaurant_001',
          template_name: 'Restaurant Premium',
          status: 'completed',
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          generation_time: 42.5,
          variations_count: 3,
          selected_variation: 1,
          preview_url: '/preview/gen_001',
          wordpress_url: 'https://sabor-brasileiro.kenzysites.com',
          ai_credits_used: 15,
          features: ['whatsapp', 'pix', 'delivery']
        },
        {
          id: 'gen_002',
          personalization_id: 'pers_002',
          business_name: 'Clínica Saúde Total',
          industry: 'healthcare',
          template_id: 'tpl_healthcare_001',
          template_name: 'Healthcare Modern',
          status: 'completed',
          created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          generation_time: 38.2,
          variations_count: 5,
          selected_variation: 3,
          preview_url: '/preview/gen_002',
          ai_credits_used: 20,
          features: ['appointment', 'whatsapp', 'lgpd']
        },
        {
          id: 'gen_003',
          personalization_id: 'pers_003',
          business_name: 'TechShop Brasil',
          industry: 'ecommerce',
          template_id: 'tpl_ecommerce_001',
          template_name: 'E-commerce Pro',
          status: 'processing',
          created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          generation_time: 0,
          variations_count: 0,
          ai_credits_used: 0,
          features: ['pix', 'cart', 'products']
        }
      ];
      
      setSites(mockSites);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching sites:', error);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      // In production, fetch from API
      // const response = await fetch('http://localhost:8000/api/v2/generation/stats');
      // const data = await response.json();
      
      const mockStats: SiteStats = {
        total_sites: 127,
        sites_this_month: 45,
        total_ai_credits: 1250,
        average_generation_time: 38.5
      };
      
      setStats(mockStats);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const filteredSites = sites.filter(site => {
    const matchesSearch = site.business_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || site.status === filterStatus;
    const matchesIndustry = filterIndustry === 'all' || site.industry === filterIndustry;
    return matchesSearch && matchesStatus && matchesIndustry;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'processing':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'draft':
        return <FileText className="w-5 h-5 text-gray-500" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusClasses = {
      completed: 'bg-green-100 text-green-800',
      processing: 'bg-blue-100 text-blue-800',
      failed: 'bg-red-100 text-red-800',
      draft: 'bg-gray-100 text-gray-800'
    };

    const statusLabels = {
      completed: 'Concluído',
      processing: 'Processando',
      failed: 'Falhou',
      draft: 'Rascunho'
    };

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${statusClasses[status as keyof typeof statusClasses]}`}>
        {getStatusIcon(status)}
        {statusLabels[status as keyof typeof statusLabels]}
      </span>
    );
  };

  const getIndustryLabel = (industry: string) => {
    const labels: Record<string, string> = {
      restaurant: 'Restaurante',
      healthcare: 'Saúde',
      ecommerce: 'E-commerce',
      services: 'Serviços',
      education: 'Educação'
    };
    return labels[industry] || industry;
  };

  const getIndustryIcon = (industry: string) => {
    const icons: Record<string, ReactElement> = {
      restaurant: <span className="text-orange-500">🍴</span>,
      healthcare: <span className="text-blue-500">🏥</span>,
      ecommerce: <span className="text-purple-500">🛒</span>,
      services: <span className="text-green-500">🔧</span>,
      education: <span className="text-indigo-500">📚</span>
    };
    return icons[industry] || <Globe className="w-4 h-4" />;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      return `Há ${diffInMinutes} minutos`;
    } else if (diffInHours < 24) {
      return `Há ${diffInHours} horas`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `Há ${diffInDays} dias`;
    }
  };

  const handleAction = (action: string, siteId: string) => {
    switch (action) {
      case 'view':
        router.push(`/sites/generated/${siteId}`);
        break;
      case 'preview':
        window.open(`/preview/${siteId}`, '_blank');
        break;
      case 'variations':
        router.push(`/generation/variations/${siteId}`);
        break;
      case 'duplicate':
        console.log('Duplicate site:', siteId);
        break;
      case 'delete':
        if (confirm('Tem certeza que deseja excluir este site?')) {
          setSites(sites.filter(s => s.id !== siteId));
        }
        break;
      case 'export':
        const site = sites.find(s => s.id === siteId);
        if (site) {
          window.open(`http://localhost:8000/api/v2/generation/export/${site.personalization_id}`, '_blank');
        }
        break;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Sites Gerados com IA</h1>
              <p className="mt-1 text-sm text-gray-500">
                Gerencie todos os sites criados automaticamente pelo KenzySites
              </p>
            </div>
            <button
              onClick={() => router.push('/generation')}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Zap className="w-5 h-5" />
              Gerar Novo Site
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total de Sites</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_sites}</p>
                </div>
                <Globe className="w-8 h-8 text-blue-500" />
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Sites Este Mês</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.sites_this_month}</p>
                </div>
                <Calendar className="w-8 h-8 text-green-500" />
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Créditos IA Usados</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_ai_credits}</p>
                </div>
                <Zap className="w-8 h-8 text-purple-500" />
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Tempo Médio</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.average_generation_time.toFixed(1)}s</p>
                </div>
                <Clock className="w-8 h-8 text-orange-500" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Buscar por nome do negócio..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div className="w-full lg:w-48">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Todos os Status</option>
                <option value="completed">Concluído</option>
                <option value="processing">Processando</option>
                <option value="failed">Falhou</option>
                <option value="draft">Rascunho</option>
              </select>
            </div>

            {/* Industry Filter */}
            <div className="w-full lg:w-48">
              <select
                value={filterIndustry}
                onChange={(e) => setFilterIndustry(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Todas as Indústrias</option>
                <option value="restaurant">Restaurante</option>
                <option value="healthcare">Saúde</option>
                <option value="ecommerce">E-commerce</option>
                <option value="services">Serviços</option>
                <option value="education">Educação</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Sites List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        ) : filteredSites.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <Globe className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum site encontrado
            </h3>
            <p className="text-gray-500 mb-6">
              {searchTerm || filterStatus !== 'all' || filterIndustry !== 'all'
                ? 'Tente ajustar os filtros de busca'
                : 'Comece gerando seu primeiro site com IA'}
            </p>
            {!searchTerm && filterStatus === 'all' && filterIndustry === 'all' && (
              <button
                onClick={() => router.push('/generation')}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Zap className="w-5 h-5" />
                Gerar Primeiro Site
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredSites.map((site) => (
              <div
                key={site.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    {/* Site Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="text-2xl">{getIndustryIcon(site.industry)}</div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {site.business_name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {getIndustryLabel(site.industry)} • Template: {site.template_name}
                          </p>
                        </div>
                      </div>
                      
                      {/* Status and Meta */}
                      <div className="flex items-center gap-4 mt-4">
                        {getStatusBadge(site.status)}
                        <span className="text-sm text-gray-500 flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {formatDate(site.created_at)}
                        </span>
                        {site.generation_time > 0 && (
                          <span className="text-sm text-gray-500 flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {site.generation_time.toFixed(1)}s
                          </span>
                        )}
                        {site.ai_credits_used > 0 && (
                          <span className="text-sm text-gray-500 flex items-center gap-1">
                            <Zap className="w-4 h-4" />
                            {site.ai_credits_used} créditos
                          </span>
                        )}
                      </div>

                      {/* Features */}
                      {site.features.length > 0 && (
                        <div className="flex items-center gap-2 mt-3">
                          <span className="text-sm text-gray-500">Features:</span>
                          <div className="flex gap-2">
                            {site.features.includes('whatsapp') && (
                              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                WhatsApp
                              </span>
                            )}
                            {site.features.includes('pix') && (
                              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                PIX
                              </span>
                            )}
                            {site.features.includes('lgpd') && (
                              <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                                LGPD
                              </span>
                            )}
                            {site.features.includes('delivery') && (
                              <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                                Delivery
                              </span>
                            )}
                            {site.features.includes('appointment') && (
                              <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full">
                                Agendamento
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Variations Info */}
                      {site.status === 'completed' && (
                        <div className="flex items-center gap-4 mt-3 pt-3 border-t">
                          <span className="text-sm text-gray-600 flex items-center gap-1">
                            <Layers className="w-4 h-4" />
                            {site.variations_count} variações geradas
                          </span>
                          {site.selected_variation && (
                            <span className="text-sm text-gray-600">
                              Variação #{site.selected_variation} selecionada
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      {site.status === 'completed' && (
                        <>
                          <button
                            onClick={() => handleAction('preview', site.id)}
                            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                            title="Preview"
                          >
                            <Eye className="w-5 h-5 text-gray-600" />
                          </button>
                          <button
                            onClick={() => handleAction('variations', site.id)}
                            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                            title="Ver Variações"
                          >
                            <Palette className="w-5 h-5 text-gray-600" />
                          </button>
                          {site.wordpress_url && (
                            <a
                              href={site.wordpress_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                              title="Abrir Site"
                            >
                              <ExternalLink className="w-5 h-5 text-gray-600" />
                            </a>
                          )}
                        </>
                      )}
                      
                      {/* Dropdown Menu */}
                      <div className="relative">
                        <button
                          onClick={() => setSelectedSite(selectedSite === site.id ? null : site.id)}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <MoreVertical className="w-5 h-5 text-gray-600" />
                        </button>
                        
                        {selectedSite === site.id && (
                          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-10">
                            <button
                              onClick={() => {
                                handleAction('view', site.id);
                                setSelectedSite(null);
                              }}
                              className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
                            >
                              <Eye className="w-4 h-4" />
                              Ver Detalhes
                            </button>
                            {site.status === 'completed' && (
                              <>
                                <button
                                  onClick={() => {
                                    handleAction('export', site.id);
                                    setSelectedSite(null);
                                  }}
                                  className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
                                >
                                  <Download className="w-4 h-4" />
                                  Exportar Configuração
                                </button>
                                <button
                                  onClick={() => {
                                    handleAction('duplicate', site.id);
                                    setSelectedSite(null);
                                  }}
                                  className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
                                >
                                  <Copy className="w-4 h-4" />
                                  Duplicar
                                </button>
                              </>
                            )}
                            <hr className="my-1" />
                            <button
                              onClick={() => {
                                handleAction('delete', site.id);
                                setSelectedSite(null);
                              }}
                              className="w-full px-4 py-2 text-left text-sm hover:bg-red-50 text-red-600 flex items-center gap-2"
                            >
                              <Trash2 className="w-4 h-4" />
                              Excluir
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}