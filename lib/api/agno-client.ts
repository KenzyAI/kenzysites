/**
 * Agno Framework API Client
 * TypeScript client for communicating with FastAPI backend
 */

// API Response Types
interface AIResponse {
  success: boolean;
  content?: string;
  message: string;
  credits_used: number;
  model_used?: string;
  processing_time?: number;
  metadata?: Record<string, any>;
  created_at: string;
}

interface AICreditsBalance {
  user_id: string;
  plan: string;
  monthly_limit: number;
  current_balance: number;
  used_this_month: number;
  reset_date: string;
  last_updated: string;
}

interface AgnoSystemStatus {
  initialized: boolean;
  total_agents: number;
  healthy_agents: number;
  primary_model?: string;
  secondary_models: number;
  agents: Array<{
    agent_name: string;
    status: string;
    last_used?: string;
    total_requests: number;
    error_count: number;
    average_response_time?: number;
  }>;
  uptime?: number;
  last_health_check: string;
}

// Request Types
interface ContentGenerationRequest {
  content_type: 'blog_post' | 'page' | 'product' | 'email' | 'social' | 'meta_description';
  topic: string;
  target_audience?: string;
  tone?: 'professional' | 'casual' | 'friendly' | 'formal' | 'playful' | 'authoritative' | 'conversational';
  keywords?: string[];
  length?: 'short' | 'medium' | 'long';
  language?: string;
  custom_instructions?: string;
  include_images?: boolean;
  seo_optimized?: boolean;
}

interface SiteGenerationRequest {
  business_name: string;
  industry: string;
  business_description: string;
  target_audience?: string;
  location?: string;
  services?: string[];
  brand_colors?: string[];
  additional_pages?: string[];
  contact_info?: Record<string, string>;
}

interface BatchContentRequest {
  requests: ContentGenerationRequest[];
  user_id: string;
  priority?: 'normal' | 'high' | 'urgent';
}

class AgnoAPIClient {
  private baseURL: string;
  private apiKey?: string;

  constructor(baseURL: string = 'http://localhost:8000', apiKey?: string) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.apiKey) {
      headers.Authorization = `Bearer ${this.apiKey}`;
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  // Health Check Endpoints
  async getHealth(): Promise<{ status: string; timestamp: string; service: string; version: string }> {
    return this.request('/api/v1/health');
  }

  async getAgnoHealth(): Promise<AgnoSystemStatus> {
    return this.request('/api/v1/health/agno');
  }

  async getSystemMetrics(): Promise<Record<string, any>> {
    return this.request('/api/v1/metrics');
  }

  // Content Generation Endpoints
  async generateContent(request: ContentGenerationRequest): Promise<AIResponse> {
    return this.request('/api/v1/content/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async generateContentBatch(request: BatchContentRequest): Promise<{
    job_id: string;
    status: string;
    total_items: number;
    estimated_credits: number;
    message: string;
  }> {
    return this.request('/api/v1/content/generate/batch', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getBatchStatus(jobId: string): Promise<{
    job_id: string;
    total_items: number;
    completed_items: number;
    failed_items: number;
    status: string;
    created_at: string;
    estimated_completion?: string;
  }> {
    return this.request(`/api/v1/content/batch/${jobId}/status`);
  }

  async optimizeContentSEO(
    content: string,
    targetKeywords: string[] = []
  ): Promise<AIResponse> {
    return this.request('/api/v1/content/optimize-seo', {
      method: 'POST',
      body: JSON.stringify({
        content,
        target_keywords: targetKeywords,
      }),
    });
  }

  async getContentTemplates(): Promise<Array<{
    id: string;
    name: string;
    description: string;
    category: string;
    estimated_credits: number;
  }>> {
    return this.request('/api/v1/content/templates');
  }

  async getContentStats(): Promise<Record<string, any>> {
    return this.request('/api/v1/content/stats');
  }

  // Site Generation Endpoints
  async generateSite(request: SiteGenerationRequest): Promise<AIResponse> {
    return this.request('/api/v1/sites/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async generateSiteAsync(request: SiteGenerationRequest): Promise<{
    job_id: string;
    status: string;
    estimated_credits: number;
    estimated_time_minutes: number;
    message: string;
  }> {
    return this.request('/api/v1/sites/generate/async', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getSiteGenerationStatus(jobId: string): Promise<{
    job_id: string;
    status: string;
    progress_percent: number;
    estimated_time_remaining_minutes: number;
    current_step: string;
    completed_steps: string[];
  }> {
    return this.request(`/api/v1/sites/generate/${jobId}/status`);
  }

  async analyzeBusiness(
    businessDescription: string,
    industry?: string
  ): Promise<{
    business_analysis: string;
    estimated_generation_time: string;
    estimated_credits: number;
    recommended_plan: string;
  }> {
    return this.request('/api/v1/sites/analyze', {
      method: 'POST',
      body: JSON.stringify({
        business_description: businessDescription,
        industry,
      }),
    });
  }

  async getSiteTemplates(): Promise<Array<{
    id: string;
    name: string;
    description: string;
    industry: string;
    pages: string[];
    features: string[];
    theme_suggestion: string;
    estimated_credits: number;
  }>> {
    return this.request('/api/v1/sites/templates');
  }

  async getRecommendedThemes(): Promise<Array<{
    name: string;
    description: string;
    features: string[];
    use_cases: string[];
    compatibility_score: number;
  }>> {
    return this.request('/api/v1/sites/themes');
  }

  async getSiteStats(): Promise<Record<string, any>> {
    return this.request('/api/v1/sites/stats');
  }

  // AI Credits System Endpoints
  async getAICreditsBalance(): Promise<AICreditsBalance> {
    return this.request('/api/v1/ai-credits/balance');
  }

  async getAICreditsTransactions(limit = 50): Promise<Array<{
    user_id: string;
    action: string;
    credits_used: number;
    remaining_balance: number;
    timestamp: string;
    details?: Record<string, any>;
  }>> {
    return this.request(`/api/v1/ai-credits/transactions?limit=${limit}`);
  }

  async getAICreditsCosts(): Promise<Record<string, number>> {
    return this.request('/api/v1/ai-credits/costs');
  }

  async getUsageStatistics(): Promise<Record<string, any>> {
    return this.request('/api/v1/ai-credits/usage-stats');
  }

  async getPlanComparison(): Promise<Array<{
    plan_name: string;
    ai_credits_monthly: number;
    price_brl_monthly: string;
    price_usd_monthly: string;
    estimated_usage: Record<string, number>;
    best_for: string;
  }>> {
    return this.request('/api/v1/ai-credits/plan-comparison');
  }

  async purchaseAdditionalCredits(creditsAmount: number): Promise<{
    transaction_id: string;
    credits_purchased: number;
    price_brl: string;
    price_usd: string;
    status: string;
    payment_url: string;
    expires_at: string;
  }> {
    return this.request('/api/v1/ai-credits/purchase-credits', {
      method: 'POST',
      body: JSON.stringify({ credits_amount: creditsAmount }),
    });
  }

  async getUsageRecommendations(): Promise<Record<string, any>> {
    return this.request('/api/v1/ai-credits/recommendations');
  }

  async getPlanLimits(): Promise<{
    plan_name: string;
    ai_credits_monthly: number;
    sites_wordpress: number;
    landing_pages: number;
    blog_posts_monthly: number;
    cloning_monthly: number;
    storage_gb: number;
    bandwidth_gb: number;
    users: number;
    white_label: boolean;
    api_access?: string;
  }> {
    return this.request('/api/v1/ai-credits/limits');
  }
}

// Create singleton instance
const agnoClient = new AgnoAPIClient(
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
);

export default agnoClient;

// Export types for use in components
export type {
  AIResponse,
  AICreditsBalance,
  AgnoSystemStatus,
  ContentGenerationRequest,
  SiteGenerationRequest,
  BatchContentRequest,
};

// Export class for custom instances
export { AgnoAPIClient };