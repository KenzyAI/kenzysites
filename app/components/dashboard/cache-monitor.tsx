"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/lib/use-toast';
import {
  Database,
  Trash2,
  RefreshCw,
  Activity,
  TrendingUp,
  Clock,
  HardDrive,
  Zap,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface CacheStats {
  stats: {
    connected_clients?: number;
    used_memory?: string;
    total_commands_processed?: number;
    keyspace_hits?: number;
    keyspace_misses?: number;
    hit_rate?: string;
    cache_type?: string;
  };
  key_counts: Record<string, number>;
  total_keys: number;
  cache_status: 'redis' | 'memory';
}

const CacheMonitor: React.FC = () => {
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const { toast } = useToast();

  const fetchCacheStats = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v2/generation/cache/stats');
      if (response.ok) {
        const data = await response.json();
        setCacheStats(data);
        setLastUpdate(new Date());
      } else {
        throw new Error('Failed to fetch cache stats');
      }
    } catch (error) {
      console.error('Error fetching cache stats:', error);
      toast({
        title: "Erro ao buscar estatísticas",
        description: "Não foi possível carregar as estatísticas do cache.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const clearCache = async () => {
    setIsClearing(true);
    try {
      const response = await fetch('http://localhost:8000/api/v2/generation/cache/clear', {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Cache limpo com sucesso! 🧹",
          description: "Todas as entradas em cache foram removidas.",
        });
        
        // Refresh stats
        await fetchCacheStats();
      } else {
        throw new Error('Failed to clear cache');
      }
    } catch (error) {
      console.error('Error clearing cache:', error);
      toast({
        title: "Erro ao limpar cache",
        description: "Não foi possível limpar o cache.",
        variant: "destructive"
      });
    } finally {
      setIsClearing(false);
    }
  };

  useEffect(() => {
    fetchCacheStats();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchCacheStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatMemory = (memory: string | undefined) => {
    if (!memory) return 'N/A';
    return memory;
  };

  const getHitRateColor = (hitRate: string | undefined) => {
    if (!hitRate || hitRate === 'N/A') return 'text-gray-500';
    const rate = parseFloat(hitRate.replace('%', ''));
    if (rate >= 80) return 'text-green-600';
    if (rate >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getHitRateProgress = (hitRate: string | undefined) => {
    if (!hitRate || hitRate === 'N/A') return 0;
    return parseFloat(hitRate.replace('%', ''));
  };

  if (!cacheStats) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            Monitor de Cache
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            {isLoading ? (
              <div className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Carregando estatísticas...</span>
              </div>
            ) : (
              <div className="text-center">
                <AlertCircle className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600">Cache não disponível</p>
                <Button
                  onClick={fetchCacheStats}
                  variant="outline"
                  size="sm"
                  className="mt-2"
                >
                  Tentar Novamente
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              Monitor de Cache
              <Badge 
                variant={cacheStats.cache_status === 'redis' ? 'default' : 'secondary'}
                className="ml-2"
              >
                {cacheStats.cache_status === 'redis' ? (
                  <>
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Redis
                  </>
                ) : (
                  'Memória'
                )}
              </Badge>
            </CardTitle>
            <div className="flex items-center gap-2">
              {lastUpdate && (
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {lastUpdate.toLocaleTimeString()}
                </span>
              )}
              <Button
                onClick={fetchCacheStats}
                variant="outline"
                size="sm"
                disabled={isLoading}
              >
                {isLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4" />
                )}
              </Button>
              <Button
                onClick={clearCache}
                variant="destructive"
                size="sm"
                disabled={isClearing}
              >
                {isClearing ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Trash2 className="w-4 h-4 mr-1" />
                    Limpar
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Hit Rate */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Taxa de Acerto</p>
                <p className={`text-2xl font-bold ${getHitRateColor(cacheStats.stats.hit_rate)}`}>
                  {cacheStats.stats.hit_rate || 'N/A'}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
            <Progress 
              value={getHitRateProgress(cacheStats.stats.hit_rate)} 
              className="mt-3"
            />
          </CardContent>
        </Card>

        {/* Total Keys */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total de Chaves</p>
                <p className="text-2xl font-bold">{cacheStats.total_keys.toLocaleString()}</p>
              </div>
              <Database className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        {/* Memory Usage */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Uso de Memória</p>
                <p className="text-2xl font-bold">{formatMemory(cacheStats.stats.used_memory)}</p>
              </div>
              <HardDrive className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        {/* Connected Clients */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Clientes Conectados</p>
                <p className="text-2xl font-bold">
                  {cacheStats.stats.connected_clients?.toLocaleString() || 'N/A'}
                </p>
              </div>
              <Activity className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Key Distribution */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Distribuição de Chaves por Tipo
          </CardTitle>
        </CardHeader>
        <CardContent>
          {Object.keys(cacheStats.key_counts).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(cacheStats.key_counts)
                .sort(([, a], [, b]) => b - a)
                .map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="capitalize">
                        {type.replace('_', ' ')}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{count.toLocaleString()}</span>
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{
                            width: `${Math.min((count / cacheStats.total_keys) * 100, 100)}%`
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-muted-foreground">Nenhuma chave encontrada no cache</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Additional Stats */}
      {cacheStats.cache_status === 'redis' && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle>Estatísticas Detalhadas (Redis)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Comandos Processados</p>
                <p className="text-lg font-semibold">
                  {cacheStats.stats.total_commands_processed?.toLocaleString() || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Cache Hits</p>
                <p className="text-lg font-semibold text-green-600">
                  {cacheStats.stats.keyspace_hits?.toLocaleString() || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Cache Misses</p>
                <p className="text-lg font-semibold text-red-600">
                  {cacheStats.stats.keyspace_misses?.toLocaleString() || 'N/A'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CacheMonitor;