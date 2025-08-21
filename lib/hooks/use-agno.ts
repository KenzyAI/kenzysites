/**
 * React hooks for Agno Framework integration
 * Provides easy-to-use hooks for AI operations
 */

import { useState, useCallback, useEffect } from 'react';
import agnoClient, { 
  AIResponse, 
  ContentGenerationRequest, 
  SiteGenerationRequest,
  AICreditsBalance,
  AgnoSystemStatus 
} from '@/lib/api/agno-client';
import { toast } from '@/components/ui/use-toast';

// Custom hook for AI Credits management
export function useAICredits() {
  const [balance, setBalance] = useState<AICreditsBalance | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBalance = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const balanceData = await agnoClient.getAICreditsBalance();
      setBalance(balanceData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch AI credits balance';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBalance();
  }, [fetchBalance]);

  const refreshBalance = useCallback(() => {
    fetchBalance();
  }, [fetchBalance]);

  return {
    balance,
    loading,
    error,
    refreshBalance,
  };
}

// Custom hook for content generation
export function useContentGeneration() {
  const [loading, setLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<AIResponse | null>(null);

  const generateContent = useCallback(async (request: ContentGenerationRequest) => {
    setLoading(true);
    
    try {
      const response = await agnoClient.generateContent(request);
      setLastResponse(response);

      if (response.success) {
        toast({
          title: "Content Generated! 🎉",
          description: `Used ${response.credits_used} AI Credits. Generated with ${response.model_used}`,
        });
      } else {
        toast({
          title: "Generation Failed",
          description: response.message,
          variant: "destructive",
        });
      }

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Content generation failed';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const optimizeSEO = useCallback(async (content: string, keywords: string[] = []) => {
    setLoading(true);
    
    try {
      const response = await agnoClient.optimizeContentSEO(content, keywords);
      
      if (response.success) {
        toast({
          title: "SEO Optimization Complete! ⚡",
          description: `Used ${response.credits_used} AI Credits`,
        });
      }

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'SEO optimization failed';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    generateContent,
    optimizeSEO,
    loading,
    lastResponse,
  };
}

// Custom hook for site generation
export function useSiteGeneration() {
  const [loading, setLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<AIResponse | null>(null);
  const [generationProgress, setGenerationProgress] = useState<{
    jobId?: string;
    status?: string;
    progress?: number;
    currentStep?: string;
  }>({});

  const generateSite = useCallback(async (request: SiteGenerationRequest, useAsync = false) => {
    setLoading(true);
    
    try {
      if (useAsync) {
        // Async generation with progress tracking
        const asyncResponse = await agnoClient.generateSiteAsync(request);
        
        setGenerationProgress({
          jobId: asyncResponse.job_id,
          status: asyncResponse.status,
          progress: 0,
          currentStep: "Starting site generation...",
        });

        toast({
          title: "Site Generation Started! 🚀",
          description: `Estimated time: ${asyncResponse.estimated_time_minutes} minutes`,
        });

        // Start polling for progress
        pollGenerationProgress(asyncResponse.job_id);
        
        return asyncResponse;
      } else {
        // Synchronous generation
        const response = await agnoClient.generateSite(request);
        setLastResponse(response);

        if (response.success) {
          toast({
            title: "Site Generated! 🎉",
            description: `Complete site created in ${response.processing_time?.toFixed(1)}s using ${response.credits_used} AI Credits`,
          });
        } else {
          toast({
            title: "Generation Failed",
            description: response.message,
            variant: "destructive",
          });
        }

        return response;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Site generation failed';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      throw err;
    } finally {
      if (!useAsync) {
        setLoading(false);
      }
    }
  }, []);

  const pollGenerationProgress = useCallback(async (jobId: string) => {
    try {
      const statusResponse = await agnoClient.getSiteGenerationStatus(jobId);
      
      setGenerationProgress({
        jobId,
        status: statusResponse.status,
        progress: statusResponse.progress_percent,
        currentStep: statusResponse.current_step,
      });

      if (statusResponse.status === 'completed') {
        setLoading(false);
        toast({
          title: "Site Generation Complete! ✅",
          description: "Your WordPress site has been successfully generated",
        });
      } else if (statusResponse.status === 'failed') {
        setLoading(false);
        toast({
          title: "Generation Failed",
          description: "Site generation encountered an error",
          variant: "destructive",
        });
      } else if (statusResponse.status === 'processing') {
        // Continue polling every 5 seconds
        setTimeout(() => pollGenerationProgress(jobId), 5000);
      }
    } catch (err) {
      console.error('Failed to poll generation progress:', err);
    }
  }, []);

  const analyzeBusiness = useCallback(async (description: string, industry?: string) => {
    try {
      const analysis = await agnoClient.analyzeBusiness(description, industry);
      
      toast({
        title: "Business Analysis Complete! 📊",
        description: `Recommended plan: ${analysis.recommended_plan}`,
      });

      return analysis;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Business analysis failed';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      throw err;
    }
  }, []);

  return {
    generateSite,
    analyzeBusiness,
    loading,
    lastResponse,
    generationProgress,
  };
}

// Custom hook for Agno system health
export function useAgnoHealth() {
  const [status, setStatus] = useState<AgnoSystemStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const healthStatus = await agnoClient.getAgnoHealth();
      setStatus(healthStatus);
      
      if (!healthStatus.initialized) {
        toast({
          title: "System Status",
          description: "Agno Framework is initializing...",
          variant: "destructive",
        });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Health check failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    status,
    loading,
    error,
    checkHealth,
    isHealthy: status?.initialized && status?.healthy_agents === status?.total_agents,
  };
}

// Custom hook for batch operations
export function useBatchOperations() {
  const [batchJobs, setBatchJobs] = useState<Map<string, any>>(new Map());
  const [loading, setLoading] = useState(false);

  const startBatchContentGeneration = useCallback(async (requests: ContentGenerationRequest[]) => {
    setLoading(true);
    
    try {
      const batchRequest = {
        requests,
        user_id: 'current_user', // Would come from auth context
        priority: 'normal' as const,
      };

      const response = await agnoClient.generateContentBatch(batchRequest);
      
      setBatchJobs(prev => new Map(prev.set(response.job_id, {
        ...response,
        startTime: new Date(),
      })));

      toast({
        title: "Batch Processing Started! 📦",
        description: `Processing ${response.total_items} items. Estimated credits: ${response.estimated_credits}`,
      });

      // Start monitoring this job
      monitorBatchJob(response.job_id);
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Batch operation failed';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const monitorBatchJob = useCallback(async (jobId: string) => {
    try {
      const status = await agnoClient.getBatchStatus(jobId);
      
      setBatchJobs(prev => {
        const updated = new Map(prev);
        const existingJob = updated.get(jobId) || {};
        updated.set(jobId, { ...existingJob, ...status });
        return updated;
      });

      if (status.status === 'completed') {
        toast({
          title: "Batch Processing Complete! ✅",
          description: `${status.completed_items}/${status.total_items} items processed successfully`,
        });
      } else if (status.status === 'processing') {
        // Continue monitoring
        setTimeout(() => monitorBatchJob(jobId), 10000);
      }
    } catch (err) {
      console.error('Failed to monitor batch job:', err);
    }
  }, []);

  return {
    startBatchContentGeneration,
    batchJobs: Array.from(batchJobs.values()),
    loading,
  };
}

// Utility hook for getting templates and static data
export function useAgnoData() {
  const [contentTemplates, setContentTemplates] = useState<any[]>([]);
  const [siteTemplates, setSiteTemplates] = useState<any[]>([]);
  const [themes, setThemes] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    
    try {
      const [contentTmpl, siteTmpl, themeData] = await Promise.all([
        agnoClient.getContentTemplates(),
        agnoClient.getSiteTemplates(),
        agnoClient.getRecommendedThemes(),
      ]);

      setContentTemplates(contentTmpl);
      setSiteTemplates(siteTmpl);
      setThemes(themeData);
    } catch (err) {
      console.error('Failed to load Agno data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return {
    contentTemplates,
    siteTemplates,
    themes,
    loading,
    refresh: loadData,
  };
}