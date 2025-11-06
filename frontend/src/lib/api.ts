import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for our API
export interface Prompt {
  id: string;
  title: string;
  description: string;
  content: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface PromptVersion {
  id: string;
  prompt_id: string;
  version_number: number;
  content: string;
  change_notes: string;
  created_at: string;
}

export interface LLMConfig {
  id: string;
  name: string;
  provider: string;
  model: string;
  temperature: string;
  max_tokens: number;
  is_active: boolean;
  created_at: string;
}

export interface Comparison {
  id: string;
  name: string;
  description: string;
  type: string;
  input_text: string;
  llm_config_id?: string;
  save_snapshot: boolean;
  results?: any[];
  successful_executions: number;
  total_executions: number;
  average_execution_time_ms: number;
  total_tokens_used: number;
  created_at: string;
  updated_at: string;
}

export interface ComparisonResult {
  version_id: string;
  version_number: number;
  prompt_content: string;
  execution_result: {
    success: boolean;
    content: string;
    usage: { total_tokens: number };
    model: string;
    execution_time_ms: number;
    tokens_used: number;
  };
  success: boolean;
  execution_time_ms: number;
  tokens_used: number;
  error_message?: string;
  created_at: string;
}

// API Functions
export const promptsApi = {
  getPrompts: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    tags?: string[];
  }) => {
    const response = await api.get('/api/v1/prompts', { params });
    return response.data;
  },
  
  getPrompt: async (id: string) => {
    const response = await api.get(`/api/v1/prompts/${id}`);
    return response.data;
  },
  
  createPrompt: async (data: {
    title: string;
    description: string;
    content: string;
    tags: string[];
  }) => {
    const response = await api.post('/api/v1/prompts', data);
    return response.data;
  },
  
  updatePrompt: async (id: string, data: {
    title?: string;
    description?: string;
    content?: string;
    tags?: string[];
  }) => {
    const response = await api.put(`/api/v1/prompts/${id}`, data);
    return response.data;
  },
  
  deletePrompt: async (id: string) => {
    await api.delete(`/api/v1/prompts/${id}`);
  },
};

export const promptVersionsApi = {
  getVersions: async (promptId: string) => {
    const response = await api.get(`/api/v1/prompts/${promptId}/versions`);
    return response.data;
  },
  
  getVersion: async (promptId: string, versionId: string) => {
    const response = await api.get(`/api/v1/prompts/${promptId}/versions/${versionId}`);
    return response.data;
  },
  
  createVersion: async (promptId: string, data: {
    content: string;
    change_notes: string;
  }) => {
    const response = await api.post(`/api/v1/prompts/${promptId}/versions`, data);
    return response.data;
  },
  
  compareVersions: async (promptId: string, versionA: string, versionB: string) => {
    const response = await api.get(
      `/api/v1/prompts/${promptId}/versions/compare`,
      { params: { version_a: versionA, version_b: versionB } }
    );
    return response.data;
  },
};

export const llmConfigsApi = {
  getConfigs: async () => {
    const response = await api.get('/api/v1/llm-configs');
    return response.data;
  },
  
  createConfig: async (data: {
    provider: string;
    api_key: string;
    model: string;
    temperature: number;
    max_tokens: number;
    active: boolean;
  }) => {
    const response = await api.post('/api/v1/llm-configs', data);
    return response.data;
  },
};

export const comparisonsApi = {
  getComparisons: async (params?: { page?: number; limit?: number }) => {
    const response = await api.get('/api/v1/comparisons', { params });
    return response.data;
  },
  
  getComparison: async (id: string) => {
    const response = await api.get(`/api/v1/comparisons/${id}`);
    return response.data;
  },
  
  createSameLLMComparison: async (data: {
    comparison_data: {
      name: string;
      description?: string;
      type: string;
      input_text: string;
      llm_config_id: string;
      save_snapshot: boolean;
    };
    prompt_version_ids: string[];
  }) => {
    const response = await api.post('/api/v1/comparisons/same-llm', data);
    return response.data;
  },
  
  createDifferentLLMComparison: async (
    promptVersionId: string,
    llmConfigIds: string[],
    inputText: string,
    name?: string,
    description?: string
  ) => {
    const params = new URLSearchParams({
      prompt_version_id: promptVersionId,
      input_text: inputText,
    });
    
    if (name) params.append('name', name);
    if (description) params.append('description', description);
    
    const response = await api.post(
      `/api/v1/comparisons/different-llm?${params.toString()}`,
      llmConfigIds
    );
    return response.data;
  },
  
  getComparisonResults: async (id: string) => {
    const response = await api.get(`/api/v1/comparisons/${id}/results`);
    return response.data;
  },
  
  getComparisonSummary: async (id: string) => {
    const response = await api.get(`/api/v1/comparisons/${id}/summary`);
    return response.data;
  },
  
  getQualityAnalysis: async (id: string) => {
    const response = await api.get(`/api/v1/comparisons/${id}/quality-analysis`);
    return response.data;
  },
  
  retryComparison: async (id: string) => {
    const response = await api.post(`/api/v1/comparisons/${id}/retry`);
    return response.data;
  },
};
