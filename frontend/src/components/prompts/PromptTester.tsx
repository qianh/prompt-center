import React, { useState, useEffect } from 'react';
import { Play, Loader, CheckCircle, XCircle, Clock, Zap } from 'lucide-react';
import { llmConfigsApi, LLMConfig } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface PromptTesterProps {
  promptContent: string;
  onClose: () => void;
}

interface TestResult {
  configId: string;
  provider: string;
  model: string;
  status: 'pending' | 'running' | 'success' | 'error';
  result?: string;
  error?: string;
  executionTime?: number;
  tokensUsed?: number;
}

export const PromptTester: React.FC<PromptTesterProps> = ({
  promptContent,
  onClose,
}) => {
  const [llmConfigs, setLlmConfigs] = useState<LLMConfig[]>([]);
  const [selectedConfigs, setSelectedConfigs] = useState<string[]>([]);
  const [testInput, setTestInput] = useState('');
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    loadLLMConfigs();
  }, []);

  const loadLLMConfigs = async () => {
    try {
      const response = await llmConfigsApi.getConfigs({ active: true });
      setLlmConfigs(response.items || []);
    } catch (error) {
      console.error('Failed to load LLM configs:', error);
    }
  };

  const toggleConfig = (configId: string) => {
    setSelectedConfigs(prev =>
      prev.includes(configId)
        ? prev.filter(id => id !== configId)
        : [...prev, configId]
    );
  };

  const runTests = async () => {
    if (!testInput.trim() || selectedConfigs.length === 0) return;

    setTesting(true);
    const results: TestResult[] = selectedConfigs.map(id => {
      const config = llmConfigs.find(c => c.id === id)!;
      return {
        configId: id,
        provider: config.provider,
        model: config.model,
        status: 'pending' as const,
      };
    });
    setTestResults(results);

    // Run tests in parallel
    const testPromises = selectedConfigs.map(async (configId, index) => {
      const config = llmConfigs.find(c => c.id === configId)!;

      // Update status to running
      setTestResults(prev =>
        prev.map((r, i) =>
          i === index ? { ...r, status: 'running' } : r
        )
      );

      try {
        const startTime = Date.now();

        // Format the prompt with the test input
        const finalPrompt = promptContent.replace(/\{input\}/g, testInput);

        // Call the LLM API
        const response = await fetch('http://localhost:8000/api/v1/llm/test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            llm_config_id: configId,
            prompt: finalPrompt,
          }),
        });

        const data = await response.json();
        const executionTime = Date.now() - startTime;

        setTestResults(prev =>
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
        setTestResults(prev =>
          prev.map((r, i) =>
            i === index
              ? {
                  ...r,
                  status: 'error',
                  error: error.message || 'Test failed',
                }
              : r
          )
        );
      }
    });

    await Promise.all(testPromises);
    setTesting(false);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Quick LLM Test
            </CardTitle>
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Test Input */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Test Input <span className="text-gray-500">(replaces {'{input}'} in prompt)</span>
            </label>
            <textarea
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
              placeholder="Enter test input..."
              className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* LLM Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Select LLMs to Test ({selectedConfigs.length} selected)
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-64 overflow-y-auto">
              {llmConfigs.map(config => (
                <label
                  key={config.id}
                  className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedConfigs.includes(config.id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedConfigs.includes(config.id)}
                    onChange={() => toggleConfig(config.id)}
                    className="mr-3"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate capitalize">
                      {config.provider}
                    </div>
                    <div className="text-xs text-gray-600 truncate">
                      {config.model}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Run Button */}
          <Button
            onClick={runTests}
            disabled={testing || !testInput.trim() || selectedConfigs.length === 0}
            className="w-full flex items-center justify-center gap-2"
          >
            {testing ? (
              <>
                <Loader className="h-4 w-4 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Run Test on {selectedConfigs.length} LLM{selectedConfigs.length !== 1 ? 's' : ''}
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Test Results */}
      {testResults.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Test Results</h3>
          {testResults.map((result, index) => (
            <Card key={index}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {result.status === 'pending' && (
                      <Clock className="h-5 w-5 text-gray-400" />
                    )}
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
                      <div className="font-medium capitalize">{result.provider}</div>
                      <div className="text-sm text-gray-600">{result.model}</div>
                    </div>
                  </div>
                  {result.status === 'success' && (
                    <div className="flex gap-4 text-sm text-gray-600">
                      <span>⏱️ {result.executionTime}ms</span>
                      {result.tokensUsed && <span>🔤 {result.tokensUsed} tokens</span>}
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {result.status === 'success' && result.result && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <pre className="whitespace-pre-wrap text-sm">{result.result}</pre>
                  </div>
                )}
                {result.status === 'error' && result.error && (
                  <div className="p-4 bg-red-50 text-red-800 rounded-lg">
                    <p className="text-sm">{result.error}</p>
                  </div>
                )}
                {(result.status === 'pending' || result.status === 'running') && (
                  <div className="p-4 text-gray-500 text-sm">
                    {result.status === 'pending' ? 'Waiting to start...' : 'Running test...'}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
