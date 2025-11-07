import React, { useState, useEffect } from 'react';
import { Clock, GitBranch, Eye, GitCompare, ArrowLeft, Zap, Edit } from 'lucide-react';
import { promptVersionsApi, PromptVersion } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Prompt } from '@/lib/api';
import { VersionLLMCompare } from './VersionLLMCompare';

interface VersionManagerProps {
  prompt: Prompt;
  onBack: () => void;
  onEditVersion?: (version: PromptVersion) => void;
}

interface VersionCompareProps {
  versionA: PromptVersion;
  versionB: PromptVersion;
  comparison: any;
  onClose: () => void;
}

const VersionCompare: React.FC<VersionCompareProps> = ({
  versionA,
  versionB,
  comparison,
  onClose,
}) => {
  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center gap-2">
            <GitCompare className="h-5 w-5" />
            Version Comparison
          </CardTitle>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
        <CardDescription>
          Comparing Version {versionA.version_number} with Version {versionB.version_number}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Version A */}
          <div className="space-y-3">
            <h3 className="font-semibold text-lg">Version {versionA.version_number}</h3>
            <div className="text-sm text-gray-500">
              {new Date(versionA.created_at).toLocaleString()}
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <pre className="whitespace-pre-wrap text-sm">{versionA.content}</pre>
            </div>
            {versionA.change_notes && (
              <div>
                <strong>Changes:</strong> {versionA.change_notes}
              </div>
            )}
          </div>

          {/* Version B */}
          <div className="space-y-3">
            <h3 className="font-semibold text-lg">Version {versionB.version_number}</h3>
            <div className="text-sm text-gray-500">
              {new Date(versionB.created_at).toLocaleString()}
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <pre className="whitespace-pre-wrap text-sm">{versionB.content}</pre>
            </div>
            {versionB.change_notes && (
              <div>
                <strong>Changes:</strong> {versionB.change_notes}
              </div>
            )}
          </div>
        </div>

        {/* Diff */}
        {comparison && comparison.diff && (
          <div className="mt-6 pt-6 border-t">
            <h3 className="font-semibold text-lg mb-3">Changes</h3>
            <div className="p-4 bg-gray-50 rounded-lg">
              <pre className="whitespace-pre-wrap text-sm font-mono">{comparison.diff}</pre>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export const VersionManager: React.FC<VersionManagerProps> = ({ prompt, onBack, onEditVersion }) => {
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCompare, setShowCompare] = useState(false);
  const [compareVersions, setCompareVersions] = useState<{
    versionA: PromptVersion;
    versionB: PromptVersion;
    comparison: any;
  } | null>(null);
  const [showLLMCompare, setShowLLMCompare] = useState(false);
  const [selectedVersions, setSelectedVersions] = useState<string[]>([]);

  useEffect(() => {
    loadVersions();
  }, []);

  const loadVersions = async () => {
    try {
      setLoading(true);
      const response = await promptVersionsApi.getVersions(prompt.id);
      // Backend returns array directly, not wrapped in {items: []}
      setVersions(Array.isArray(response) ? response : response.items || []);
    } catch (error) {
      console.error('Failed to load versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompareVersions = async (versionA: PromptVersion, versionB: PromptVersion) => {
    try {
      const comparison = await promptVersionsApi.compareVersions(
        prompt.id,
        versionA.id,
        versionB.id
      );
      setCompareVersions({
        versionA,
        versionB,
        comparison,
      });
      setShowCompare(true);
    } catch (error) {
      console.error('Failed to compare versions:', error);
    }
  };

  const toggleVersionSelection = (versionId: string) => {
    setSelectedVersions(prev =>
      prev.includes(versionId)
        ? prev.filter(id => id !== versionId)
        : [...prev, versionId]
    );
  };

  const handleStartLLMCompare = () => {
    if (selectedVersions.length >= 2) {
      setShowLLMCompare(true);
    }
  };

  if (showLLMCompare) {
    const selectedVersionsList = versions.filter(v => selectedVersions.includes(v.id));
    return (
      <VersionLLMCompare
        versions={selectedVersionsList}
        onClose={() => {
          setShowLLMCompare(false);
          setSelectedVersions([]);
        }}
      />
    );
  }

  if (showCompare && compareVersions) {
    return (
      <VersionCompare
        versionA={compareVersions.versionA}
        versionB={compareVersions.versionB}
        comparison={compareVersions.comparison}
        onClose={() => setShowCompare(false)}
      />
    );
  }

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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Prompts
          </Button>
          <div>
            <h2 className="text-2xl font-bold">Version History</h2>
            <p className="text-gray-600">{prompt.title}</p>
          </div>
        </div>
        {selectedVersions.length >= 2 && (
          <Button onClick={handleStartLLMCompare}>
            <Zap className="h-4 w-4 mr-2" />
            Compare {selectedVersions.length} Versions with LLM
          </Button>
        )}
      </div>

      {/* Versions List */}
      <div className="space-y-4">
        {versions.map((version, index) => (
          <Card key={version.id} className={selectedVersions.includes(version.id) ? 'border-blue-500 bg-blue-50' : ''}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={selectedVersions.includes(version.id)}
                    onChange={() => toggleVersionSelection(version.id)}
                    className="mt-1"
                  />
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <GitBranch className="h-5 w-5" />
                      Version {version.version_number}
                      {index === 0 && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                          Latest
                        </span>
                      )}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-2 mt-2">
                      <Clock className="h-4 w-4" />
                      {new Date(version.created_at).toLocaleString()}
                    </CardDescription>
                  </div>
                </div>
                <div className="flex gap-2">
                  {onEditVersion && (
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => onEditVersion(version)}
                    >
                      <Edit className="h-4 w-4 mr-2" />
                      Edit / Create New Version
                    </Button>
                  )}
                  {index > 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCompareVersions(versions[0], version)}
                    >
                      <GitCompare className="h-4 w-4 mr-2" />
                      Compare with Latest
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {/* Content Preview */}
                <div>
                  <strong>Content:</strong>
                  <div className="mt-2 p-3 bg-gray-50 rounded text-sm line-clamp-4">
                    <pre className="whitespace-pre-wrap">{version.content}</pre>
                  </div>
                </div>

                {/* Change Notes */}
                {version.change_notes && (
                  <div>
                    <strong>Change Notes:</strong>
                    <p className="text-sm text-gray-600 mt-1">{version.change_notes}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {versions.length === 0 && (
        <div className="text-center py-12">
          <GitBranch className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No versions found
          </h3>
          <p className="text-gray-500">
            This prompt doesn't have any version history yet.
          </p>
        </div>
      )}
    </div>
  );
};
