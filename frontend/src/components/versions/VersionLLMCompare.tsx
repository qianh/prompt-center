import React, { useState, useEffect } from 'react';
import { Play, Loader, CheckCircle, XCircle, GitCompare } from 'lucide-react';
import { llmConfigsApi, LLMConfig, PromptVersion } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface VersionLLMCompareProps {
  versions: PromptVersion[];
  onClose: () => void;
}

interface CompareResult {
  versionId: string;
  versionNumber: number;
  status: 'pending' | 'running' | 'success' | 'error';
  result?: string;
  error?: string;
  executionTime?: number;
  tokensUsed?: number;
}

export const VersionLLMCompare: React.FC<VersionLLMCompareProps> = ({
  versions,
  onClose,
}) => {
  const [llmConfigs, setLlmConfigs] = useState<LLMConfig[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<string>('');
  const [testInput, setTestInput] = useState('');
  const [compareResults, setCompareResults] = useState<CompareResult[]>([]);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    loadLLMConfigs();
  }, []);

  const loadLLMConfigs = async () => {
    try {
      const response = await llmConfigsApi.getConfigs({ active: true });
      setLlmConfigs(response.items || []);
      if (response.items && response.items.length > 0) {
        setSelectedConfig(response.items[0].id);
      }
    } catch (error) {
      console.error('Failed to load LLM configs:', error);
    }
  };

  const runComparison = async () => {
    if (!testInput.trim() || !selectedConfig || versions.length < 2) return;

    setComparing(true);
    const results: CompareResult[] = versions.map(v => ({
      versionId: v.id,
      versionNumber: v.version_number,
      status: 'pending' as const,
    }));
    setCompareResults(results);

    // Run tests in parallel
    const testPromises = versions.map(async (version, index) => {
      // Update status to running
      setCompareResults(prev =>
        prev.map((r, i) =>
          i === index ? { ...r, status: 'running' } : r
        )
      );

      try {
        const startTime = Date.now();

        // Format the prompt with the test input
        const finalPrompt = version.content.replace(/\{input\}/g, testInput);

        // Call the LLM API
        const response = await fetch('http://localhost:8000/api/v1/llm/test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            llm_config_id: selectedConfig,
            prompt: finalPrompt,
          }),
        });

        const data = await response.json();
        const executionTime = Date.now() - startTime;

        setCompareResults(prev =>
          prev.map((r, i) =>
            i === index
              ? {
                  ...r,
                  status: 'success',
                  result: data.content,
                  executionTime,
                  tokensUsed: data.tokens_used,
                }
              : r
          )
        );
      } catch (error: any) {
        setCompareResults(prev =>
          prev.map((r, i) =>
            i === index
              ? {
                  ...r,
                  status: 'error',
                  error: error.message || 'Comparison failed',
                }
              : r
          )
        );
      }
    });

    await Promise.all(testPromises);
    setComparing(false);
  };

  const selectedConfigData = llmConfigs.find(c => c.id === selectedConfig);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              <GitCompare className="h-5 w-5" />
              Compare Versions with LLM
            </CardTitle>
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
          <p className="text-sm text-gray-600">
            Comparing {versions.length} versions: {versions.map(v => `v${v.version_number}`).join(', ')}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* LLM Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Select LLM</label>
            <select
              value={selectedConfig}
              onChange={(e) => setSelectedConfig(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {llmConfigs.map(config => (
                <option key={config.id} value={config.id}>
                  {config.provider} - {config.model}
                </option>
              ))}
            </select>
            {selectedConfigData && (
              <p className="text-xs text-gray-500 mt-1">
                Temp: {selectedConfigData.temperature}, Max Tokens: {selectedConfigData.max_tokens}
              </p>
            )}
          </div>

          {/* Test Input */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Test Input <span className="text-gray-500">(replaces {'{input}'} in prompts)</span>
            </label>
            <textarea
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
              placeholder="Enter test input..."
              className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Run Button */}
          <Button
            onClick={runComparison}
            disabled={comparing || !testInput.trim() || !selectedConfig}
            className="w-full flex items-center justify-center gap-2"
          >
            {comparing ? (
              <>
                <Loader className="h-4 w-4 animate-spin" />
                Comparing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Run Comparison on {versions.length} Versions
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Comparison Results */}
      {compareResults.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {compareResults.map((result, index) => {
            const version = versions.find(v => v.id === result.versionId)!;
            return (
              <Card key={index}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {result.status === 'running' && (
                        <Loader className="h-5 w-5 text-blue-500 animate-spin" />
                      )}
                      {result.status === 'success' && (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      )}
                      {result.status === 'error' && (
                        <XCircle className="h-5 w-5 text-red-500" />
                      )}
                      <div>
                        <div className="font-medium">Version {result.versionNumber}</div>
                        {version.change_notes && (
                          <div className="text-xs text-gray-500">{version.change_notes}</div>
                        )}
                      </div>
                    </div>
                    {result.status === 'success' && (
                      <div className="text-xs text-gray-600">
                        {result.executionTime}ms
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* Version Content */}
                  <div>
                    <div className="text-xs font-medium text-gray-500 mb-1">PROMPT:</div>
                    <div className="p-2 bg-gray-50 rounded text-xs">
                      <pre className="whitespace-pre-wrap">{version.content}</pre>
                    </div>
                  </div>

                  {/* Result */}
                  {result.status === 'success' && result.result && (
                    <div>
                      <div className="text-xs font-medium text-gray-500 mb-1">OUTPUT:</div>
                      <div className="p-3 bg-green-50 border border-green-200 rounded">
                        <pre className="whitespace-pre-wrap text-sm">{result.result}</pre>
                      </div>
                      {result.tokensUsed && (
                        <div className="text-xs text-gray-500 mt-1">
                          Tokens: {result.tokensUsed}
                        </div>
                      )}
                    </div>
                  )}

                  {result.status === 'error' && result.error && (
                    <div className="p-3 bg-red-50 border border-red-200 text-red-800 rounded">
                      <p className="text-sm">{result.error}</p>
                    </div>
                  )}

                  {(result.status === 'pending' || result.status === 'running') && (
                    <div className="p-3 text-gray-500 text-sm">
                      {result.status === 'pending' ? 'Waiting...' : 'Running...'}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
