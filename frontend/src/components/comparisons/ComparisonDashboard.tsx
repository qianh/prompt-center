import React, { useState, useEffect } from 'react';
import { BarChart3, RefreshCw, Plus, Eye, Trash2 } from 'lucide-react';
import { comparisonsApi, Comparison } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface ComparisonDashboardProps {
  onNewComparison: () => void;
  onViewComparison: (comparison: Comparison) => void;
}

export const ComparisonDashboard: React.FC<ComparisonDashboardProps> = ({
  onNewComparison,
  onViewComparison,
}) => {
  const [comparisons, setComparisons] = useState<Comparison[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadComparisons();
  }, []);

  const loadComparisons = async () => {
    try {
      setLoading(true);
      const response = await comparisonsApi.getComparisons();
      setComparisons(response.items || []);
    } catch (error) {
      console.error('Failed to load comparisons:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRetryComparison = async (id: string) => {
    try {
      await comparisonsApi.retryComparison(id);
      loadComparisons();
    } catch (error) {
      console.error('Failed to retry comparison:', error);
    }
  };

  const handleDeleteComparison = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this comparison?')) {
      try {
        // Note: API doesn't have delete endpoint yet, this is placeholder
        setComparisons(comparisons.filter(c => c.id !== id));
      } catch (error) {
        console.error('Failed to delete comparison:', error);
      }
    }
  };

  const getSuccessRate = (comparison: Comparison) => {
    if (comparison.total_executions === 0) return 0;
    return Math.round((comparison.successful_executions / comparison.total_executions) * 100);
  };

  const getStatusColor = (comparison: Comparison) => {
    const rate = getSuccessRate(comparison);
    if (rate === 100) return 'text-green-600 bg-green-100';
    if (rate >= 50) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Comparisons</h2>
          <p className="text-gray-600">Test and compare prompt performance</p>
        </div>
        <Button onClick={onNewComparison} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Comparison
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Comparisons</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{comparisons.length}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {comparisons.length > 0 
                ? Math.round(
                    comparisons.reduce((sum, c) => sum + getSuccessRate(c), 0) / comparisons.length
                  )
                : 0}%
            </div>
            <p className="text-xs text-muted-foreground">Average</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Tokens Used</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {comparisons.reduce((sum, c) => sum + c.total_tokens_used, 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">Across all comparisons</p>
          </CardContent>
        </Card>
      </div>

      {/* Comparisons List */}
      <div className="space-y-4">
        {comparisons.map(comparison => (
          <Card key={comparison.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    {comparison.name}
                  </CardTitle>
                  <CardDescription className="mt-2">
                    {comparison.description}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(comparison)}`}>
                    {getSuccessRate(comparison)}% Success
                  </span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {comparison.type}
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Executions:</span>
                    <div className="font-medium">
                      {comparison.successful_executions}/{comparison.total_executions}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500">Avg Time:</span>
                    <div className="font-medium">{comparison.average_execution_time_ms}ms</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Tokens:</span>
                    <div className="font-medium">{comparison.total_tokens_used.toLocaleString()}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Created:</span>
                    <div className="font-medium">
                      {new Date(comparison.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                {/* Input Preview */}
                <div>
                  <span className="text-gray-500 text-sm">Input:</span>
                  <div className="mt-1 p-2 bg-gray-50 rounded text-sm line-clamp-2">
                    {comparison.input_text}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-2">
                  {getSuccessRate(comparison) < 100 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRetryComparison(comparison.id)}
                      className="flex items-center gap-1"
                    >
                      <RefreshCw className="h-3 w-3" />
                      Retry Failed
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onViewComparison(comparison)}
                    className="flex items-center gap-1"
                  >
                    <Eye className="h-3 w-3" />
                    View Details
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDeleteComparison(comparison.id)}
                    className="flex items-center gap-1 text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-3 w-3" />
                    Delete
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {comparisons.length === 0 && (
        <div className="text-center py-12">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No comparisons yet
          </h3>
          <p className="text-gray-500 mb-4">
            Create your first comparison to test prompt performance across different versions and LLMs.
          </p>
          <Button onClick={onNewComparison}>
            <Plus className="h-4 w-4 mr-2" />
            Create Comparison
          </Button>
        </div>
      )}
    </div>
  );
};
