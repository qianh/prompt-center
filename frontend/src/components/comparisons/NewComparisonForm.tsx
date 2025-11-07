import React, { useState, useEffect } from 'react';
import { ArrowLeft, Play, TestTube } from 'lucide-react';
import { comparisonsApi, promptVersionsApi, llmConfigsApi, PromptVersion, LLMConfig } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface NewComparisonFormProps {
  onCancel: () => void;
  onCreated: () => void;
}

export const NewComparisonForm: React.FC<NewComparisonFormProps> = ({
  onCancel,
  onCreated,
}) => {
  const [comparisonType, setComparisonType] = useState<'same_llm' | 'different_llm'>('same_llm');
  const [prompts, setPrompts] = useState<any[]>([]);
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [llmConfigs, setLlmConfigs] = useState<LLMConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    input_text: '',
    selectedPromptId: '',
    selectedVersions: [] as string[],
    selectedLlmConfig: '',
    selectedLlmConfigs: [] as string[],
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      // Load prompts and LLM configs
      const [promptsResponse, configsResponse] = await Promise.all([
        fetch('http://localhost:8000/api/v1/prompts'),
        llmConfigsApi.getConfigs({ active: true }), // Only load active configs
      ]);

      const promptsData = await promptsResponse.json();
      setPrompts(promptsData.items || []);
      setLlmConfigs(configsResponse.items || []);
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  };

  const handlePromptSelect = async (promptId: string) => {
    setFormData(prev => ({ ...prev, selectedPromptId: promptId, selectedVersions: [] }));
    
    if (promptId) {
      try {
        const response = await promptVersionsApi.getVersions(promptId);
        // Backend returns array directly, not wrapped in {items: []}
        setVersions(Array.isArray(response) ? response : response.items || []);
      } catch (error) {
        console.error('Failed to load versions:', error);
        setVersions([]);
      }
    } else {
      setVersions([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (comparisonType === 'same_llm') {
        await comparisonsApi.createSameLLMComparison({
          comparison_data: {
            name: formData.name,
            description: formData.description,
            type: 'same_llm',
            input_text: formData.input_text,
            llm_config_id: formData.selectedLlmConfig,
            save_snapshot: true,
          },
          prompt_version_ids: formData.selectedVersions,
        });
      } else {
        // Different LLM comparison
        const versionId = formData.selectedVersions[0];
        if (versionId) {
          await comparisonsApi.createDifferentLLMComparison(
            versionId,
            formData.selectedLlmConfigs,
            formData.input_text,
            formData.name,
            formData.description
          );
        }
      }
      
      onCreated();
    } catch (error) {
      console.error('Failed to create comparison:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleVersion = (versionId: string) => {
    setFormData(prev => ({
      ...prev,
      selectedVersions: prev.selectedVersions.includes(versionId)
        ? prev.selectedVersions.filter(id => id !== versionId)
        : [...prev.selectedVersions, versionId]
    }));
  };

  const toggleLlmConfig = (configId: string) => {
    setFormData(prev => ({
      ...prev,
      selectedLlmConfigs: prev.selectedLlmConfigs.includes(configId)
        ? prev.selectedLlmConfigs.filter(id => id !== configId)
        : [...prev.selectedLlmConfigs, configId]
    }));
  };

  const isFormValid = () => {
    if (!formData.name || !formData.input_text || !formData.selectedPromptId) return false;
    
    if (comparisonType === 'same_llm') {
      return formData.selectedVersions.length >= 2 && formData.selectedLlmConfig;
    } else {
      return formData.selectedVersions.length === 1 && formData.selectedLlmConfigs.length >= 2;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={onCancel}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div>
          <h2 className="text-2xl font-bold">New Comparison</h2>
          <p className="text-gray-600">Test prompt performance</p>
        </div>
      </div>

      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TestTube className="h-5 w-5" />
            Comparison Configuration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Comparison Type */}
            <div>
              <label className="block text-sm font-medium mb-3">Comparison Type</label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => setComparisonType('same_llm')}
                  className={`p-4 border rounded-lg text-left transition-colors ${
                    comparisonType === 'same_llm'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium">Same LLM</div>
                  <div className="text-sm text-gray-600">
                    Compare multiple prompt versions with the same LLM
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setComparisonType('different_llm')}
                  className={`p-4 border rounded-lg text-left transition-colors ${
                    comparisonType === 'different_llm'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium">Different LLMs</div>
                  <div className="text-sm text-gray-600">
                    Compare the same prompt across different LLMs
                  </div>
                </button>
              </div>
            </div>

            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Comparison Name *
                </label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter comparison name..."
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Description
                </label>
                <Input
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe this comparison..."
                />
              </div>
            </div>

            {/* Input Text */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Test Input *
              </label>
              <textarea
                value={formData.input_text}
                onChange={(e) => setFormData(prev => ({ ...prev, input_text: e.target.value }))}
                placeholder="Enter the test input text..."
                className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {/* Prompt Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Select Prompt *
              </label>
              <select
                value={formData.selectedPromptId}
                onChange={(e) => handlePromptSelect(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Choose a prompt...</option>
                {prompts.map(prompt => (
                  <option key={prompt.id} value={prompt.id}>
                    {prompt.title}
                  </option>
                ))}
              </select>
            </div>

            {/* Version Selection */}
            {versions.length > 0 && (
              <div>
                <label className="block text-sm font-medium mb-2">
                  Select {comparisonType === 'same_llm' ? 'Prompt Versions' : 'Prompt Version'} *
                </label>
                <div className="space-y-2">
                  {versions.map(version => (
                    <label
                      key={version.id}
                      className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
                    >
                      <input
                        type={comparisonType === 'same_llm' ? 'checkbox' : 'radio'}
                        name="version"
                        checked={formData.selectedVersions.includes(version.id)}
                        onChange={() => toggleVersion(version.id)}
                        className="mr-3"
                      />
                      <div className="flex-1">
                        <div className="font-medium">Version {version.version_number}</div>
                        <div className="text-sm text-gray-600 line-clamp-2">
                          {version.content}
                        </div>
                        {version.change_notes && (
                          <div className="text-xs text-gray-500 mt-1">
                            {version.change_notes}
                          </div>
                        )}
                      </div>
                    </label>
                  ))}
                </div>
                {comparisonType === 'same_llm' && (
                  <p className="text-sm text-gray-500 mt-2">
                    Select 2 or more versions to compare
                  </p>
                )}
                {comparisonType === 'different_llm' && (
                  <p className="text-sm text-gray-500 mt-2">
                    Select 1 version to test across different LLMs
                  </p>
                )}
              </div>
            )}

            {/* LLM Configuration */}
            {llmConfigs.length > 0 && (
              <div>
                <label className="block text-sm font-medium mb-2">
                  Select {comparisonType === 'same_llm' ? 'LLM Configuration' : 'LLM Configurations'} *
                </label>
                <div className="space-y-2">
                  {llmConfigs.map(config => (
                    <label
                      key={config.id}
                      className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
                    >
                      <input
                        type={comparisonType === 'same_llm' ? 'radio' : 'checkbox'}
                        name="llm"
                        checked={
                          comparisonType === 'same_llm'
                            ? formData.selectedLlmConfig === config.id
                            : formData.selectedLlmConfigs.includes(config.id)
                        }
                        onChange={() => {
                          if (comparisonType === 'same_llm') {
                            setFormData(prev => ({ ...prev, selectedLlmConfig: config.id }));
                          } else {
                            toggleLlmConfig(config.id);
                          }
                        }}
                        className="mr-3"
                      />
                      <div className="flex-1">
                        <div className="font-medium capitalize">{config.provider} - {config.model}</div>
                        {config.base_url && (
                          <div className="text-sm text-gray-600 truncate" title={config.base_url}>
                            {config.base_url}
                          </div>
                        )}
                        <div className="text-xs text-gray-500">
                          Temp: {config.temperature}, Max Tokens: {config.max_tokens}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
                {comparisonType === 'same_llm' && (
                  <p className="text-sm text-gray-500 mt-2">
                    Select 1 LLM configuration to test all versions
                  </p>
                )}
                {comparisonType === 'different_llm' && (
                  <p className="text-sm text-gray-500 mt-2">
                    Select 2 or more LLM configurations to compare
                  </p>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={!isFormValid() || loading}
                className="flex items-center gap-2"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Run Comparison
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
