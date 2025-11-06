import React, { useState, useEffect } from 'react';
import { Plus, Settings, Trash2, Edit, Power, TestTube, Check, X, AlertCircle } from 'lucide-react';
import { llmConfigsApi, LLMConfig } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface LLMSettingsProps {
  onBack?: () => void;
}

export const LLMSettings: React.FC<LLMSettingsProps> = ({ onBack }) => {
  const [configs, setConfigs] = useState<LLMConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState<LLMConfig | null>(null);
  const [formData, setFormData] = useState({
    provider: 'openai',
    api_key: '',
    model: '',
    temperature: 0.7,
    max_tokens: 1000,
    active: true,
  });
  const [testingConnection, setTestingConnection] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      setLoading(true);
      const response = await llmConfigsApi.getConfigs();
      setConfigs(response.items || []);
    } catch (error) {
      console.error('Failed to load LLM configs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNew = () => {
    setEditingConfig(null);
    setFormData({
      provider: 'openai',
      api_key: '',
      model: '',
      temperature: 0.7,
      max_tokens: 1000,
      active: true,
    });
    setTestResult(null);
    setShowForm(true);
  };

  const handleEdit = (config: LLMConfig) => {
    setEditingConfig(config);
    setFormData({
      provider: config.provider,
      api_key: config.api_key,
      model: config.model,
      temperature: config.temperature,
      max_tokens: config.max_tokens,
      active: config.active,
    });
    setTestResult(null);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this LLM configuration?')) {
      try {
        await llmConfigsApi.deleteConfig(id);
        setConfigs(configs.filter(c => c.id !== id));
      } catch (error) {
        console.error('Failed to delete config:', error);
        alert('Failed to delete configuration');
      }
    }
  };

  const handleToggle = async (id: string) => {
    try {
      const updatedConfig = await llmConfigsApi.toggleConfig(id);
      setConfigs(configs.map(c => (c.id === id ? updatedConfig : c)));
    } catch (error) {
      console.error('Failed to toggle config:', error);
      alert('Failed to toggle configuration');
    }
  };

  const handleTestConnection = async () => {
    if (!formData.api_key || !formData.model) {
      setTestResult({ success: false, message: 'Please fill in API key and model' });
      return;
    }

    try {
      setTestingConnection(true);
      const result = await llmConfigsApi.testConnection({
        provider: formData.provider,
        api_key: formData.api_key,
        model: formData.model,
        temperature: formData.temperature,
        max_tokens: 100,
      });

      setTestResult({
        success: result.success,
        message: result.success ? result.message : result.error,
      });
    } catch (error: any) {
      setTestResult({
        success: false,
        message: error.response?.data?.error || 'Connection test failed',
      });
    } finally {
      setTestingConnection(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (editingConfig) {
        const updated = await llmConfigsApi.updateConfig(editingConfig.id, formData);
        setConfigs(configs.map(c => (c.id === editingConfig.id ? updated : c)));
      } else {
        const created = await llmConfigsApi.createConfig(formData);
        setConfigs([...configs, created]);
      }
      setShowForm(false);
      setTestResult(null);
    } catch (error: any) {
      console.error('Failed to save config:', error);
      alert(error.response?.data?.detail || 'Failed to save configuration');
    }
  };

  const getProviderLabel = (provider: string) => {
    const labels: Record<string, string> = {
      openai: 'OpenAI',
      anthropic: 'Anthropic',
      google: 'Google AI',
      mock: 'Mock (Testing)',
    };
    return labels[provider] || provider;
  };

  const getModelPlaceholder = (provider: string) => {
    const placeholders: Record<string, string> = {
      openai: 'e.g., gpt-4, gpt-3.5-turbo',
      anthropic: 'e.g., claude-3-sonnet-20240229',
      google: 'e.g., gemini-pro',
      mock: 'e.g., mock-model',
    };
    return placeholders[provider] || 'Enter model name';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (showForm) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">
            {editingConfig ? 'Edit LLM Configuration' : 'Add LLM Configuration'}
          </h2>
          <Button variant="outline" onClick={() => setShowForm(false)}>
            Cancel
          </Button>
        </div>

        <Card>
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Provider Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">Provider</label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="google">Google AI</option>
                  <option value="mock">Mock (Testing)</option>
                </select>
              </div>

              {/* API Key */}
              <div>
                <label className="block text-sm font-medium mb-2">API Key</label>
                <Input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  placeholder="Enter your API key"
                  required
                />
              </div>

              {/* Model */}
              <div>
                <label className="block text-sm font-medium mb-2">Model</label>
                <Input
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  placeholder={getModelPlaceholder(formData.provider)}
                  required
                />
              </div>

              {/* Temperature */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Temperature ({formData.temperature})
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={formData.temperature}
                  onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Focused</span>
                  <span>Balanced</span>
                  <span>Creative</span>
                </div>
              </div>

              {/* Max Tokens */}
              <div>
                <label className="block text-sm font-medium mb-2">Max Tokens</label>
                <Input
                  type="number"
                  min="1"
                  max="8000"
                  value={formData.max_tokens}
                  onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                  required
                />
              </div>

              {/* Active Status */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="active"
                  checked={formData.active}
                  onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="active" className="text-sm font-medium">
                  Active (available for use)
                </label>
              </div>

              {/* Test Connection */}
              <div className="border-t pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleTestConnection}
                  disabled={testingConnection}
                  className="w-full flex items-center justify-center gap-2"
                >
                  {testingConnection ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                      Testing Connection...
                    </>
                  ) : (
                    <>
                      <TestTube className="h-4 w-4" />
                      Test Connection
                    </>
                  )}
                </Button>

                {testResult && (
                  <div className={`mt-3 p-3 rounded-md flex items-start gap-2 ${
                    testResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
                  }`}>
                    {testResult.success ? (
                      <Check className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    ) : (
                      <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    )}
                    <div className="text-sm">{testResult.message}</div>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <div className="flex gap-3 pt-4">
                <Button type="submit" className="flex-1">
                  {editingConfig ? 'Update Configuration' : 'Create Configuration'}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">LLM Configurations</h2>
          <p className="text-gray-600 mt-1">Manage your language model provider settings</p>
        </div>
        <Button onClick={handleCreateNew} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Configuration
        </Button>
      </div>

      {/* Configurations List */}
      {configs.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No LLM Configurations</h3>
            <p className="text-gray-600 mb-4">
              Get started by adding your first LLM provider configuration
            </p>
            <Button onClick={handleCreateNew}>Add Configuration</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {configs.map((config) => (
            <Card key={config.id} className={!config.active ? 'opacity-60' : ''}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">
                        {getProviderLabel(config.provider)}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        config.active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {config.active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <div className="space-y-1 text-sm text-gray-600">
                      <p><span className="font-medium">Model:</span> {config.model}</p>
                      <p><span className="font-medium">Temperature:</span> {config.temperature}</p>
                      <p><span className="font-medium">Max Tokens:</span> {config.max_tokens}</p>
                      <p className="text-xs text-gray-400 mt-2">
                        Added {new Date(config.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggle(config.id)}
                      title={config.active ? 'Deactivate' : 'Activate'}
                    >
                      <Power className={`h-4 w-4 ${config.active ? 'text-green-600' : 'text-gray-400'}`} />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(config)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(config.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
