import React, { useState, useEffect } from 'react';
import { Save, X, Plus, Tag, Zap, GitBranch } from 'lucide-react';
import { promptsApi, promptVersionsApi, Prompt, PromptVersion } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PromptTester } from './PromptTester';

interface VersionedPromptEditorProps {
  prompt: Prompt;
  onSave: (prompt: Prompt) => void;
  onCancel: () => void;
}

interface SaveConfirmDialogProps {
  currentVersion: number;
  onConfirm: (createNew: boolean, changeNotes: string) => void;
  onCancel: () => void;
}

const SaveConfirmDialog: React.FC<SaveConfirmDialogProps> = ({
  currentVersion,
  onConfirm,
  onCancel
}) => {
  const [createNew, setCreateNew] = useState(true);
  const [changeNotes, setChangeNotes] = useState('');

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Save Changes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-sm text-gray-600">
            Current version: <span className="font-semibold">v{currentVersion}.0</span>
          </div>

          {/* Update current version option */}
          <label className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
            <input
              type="radio"
              checked={!createNew}
              onChange={() => setCreateNew(false)}
              className="mt-1"
            />
            <div>
              <div className="font-medium">Update current version (v{currentVersion}.0)</div>
              <div className="text-sm text-gray-600">Overwrite existing version</div>
            </div>
          </label>

          {/* Create new version option */}
          <label className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
            <input
              type="radio"
              checked={createNew}
              onChange={() => setCreateNew(true)}
              className="mt-1"
            />
            <div>
              <div className="font-medium">Create new version (v{currentVersion + 1}.0)</div>
              <div className="text-sm text-gray-600">Keep v{currentVersion}.0 as history</div>
            </div>
          </label>

          {/* Change notes (only for new version) */}
          {createNew && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Change Notes (Optional)
              </label>
              <textarea
                value={changeNotes}
                onChange={(e) => setChangeNotes(e.target.value)}
                placeholder="Describe what changed..."
                className="w-full h-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button onClick={() => onConfirm(createNew, changeNotes)}>
              Save
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export const VersionedPromptEditor: React.FC<VersionedPromptEditorProps> = ({
  prompt,
  onSave,
  onCancel,
}) => {
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState<string>('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    content: '',
    tags: [] as string[],
  });
  const [newTag, setNewTag] = useState('');
  const [loading, setLoading] = useState(false);
  const [showTester, setShowTester] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [versionsLoading, setVersionsLoading] = useState(true);

  useEffect(() => {
    loadVersions();
    setFormData({
      title: prompt.title,
      description: prompt.description,
      content: prompt.content,
      tags: prompt.tags,
    });
  }, [prompt]);

  const loadVersions = async () => {
    try {
      setVersionsLoading(true);
      const response = await promptVersionsApi.getVersions(prompt.id);
      const versionList = response.items || [];
      setVersions(versionList);

      // Select latest version by default
      if (versionList.length > 0) {
        const latest = versionList[0]; // Assuming sorted by version desc
        setSelectedVersionId(latest.id);
        setFormData(prev => ({
          ...prev,
          content: latest.content
        }));
      }
    } catch (error) {
      console.error('Failed to load versions:', error);
    } finally {
      setVersionsLoading(false);
    }
  };

  const handleVersionSelect = (version: PromptVersion) => {
    setSelectedVersionId(version.id);
    setFormData(prev => ({
      ...prev,
      content: version.content
    }));
  };

  const handleSaveClick = () => {
    setShowSaveDialog(true);
  };

  const handleConfirmSave = async (createNew: boolean, changeNotes: string) => {
    setLoading(true);
    setShowSaveDialog(false);

    try {
      // Update prompt metadata (title, description, tags)
      const updatedPrompt = await promptsApi.updatePrompt(prompt.id, {
        title: formData.title,
        description: formData.description,
        tags: formData.tags,
      });

      if (createNew) {
        // Create new version
        await promptVersionsApi.createVersion(prompt.id, {
          content: formData.content,
          change_notes: changeNotes,
        });
      } else {
        // Update current version
        const selectedVersion = versions.find(v => v.id === selectedVersionId);
        if (selectedVersion) {
          await promptVersionsApi.updateVersion(
            prompt.id,
            selectedVersion.id,
            {
              content: formData.content,
              change_notes: changeNotes || undefined,
            }
          );
        }
      }

      // Reload to get updated data
      await loadVersions();
      onSave(updatedPrompt);
    } catch (error) {
      console.error('Failed to save prompt:', error);
      alert('Failed to save changes');
    } finally {
      setLoading(false);
    }
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const selectedVersion = versions.find(v => v.id === selectedVersionId);
  const currentVersionNumber = selectedVersion?.version_number || prompt.latest_version;

  if (showTester) {
    return (
      <PromptTester
        promptContent={formData.content}
        onClose={() => setShowTester(false)}
      />
    );
  }

  return (
    <>
      <Card className="w-full max-w-6xl mx-auto">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <CardTitle>Edit Prompt</CardTitle>
              <span className="text-sm text-gray-500">
                {prompt.total_versions} version{prompt.total_versions !== 1 ? 's' : ''}
              </span>
            </div>
            <Button variant="ghost" size="sm" onClick={onCancel}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Version Tabs */}
          {!versionsLoading && versions.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-2">
                <GitBranch className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium">Versions:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {versions.map(version => (
                  <button
                    key={version.id}
                    onClick={() => handleVersionSelect(version)}
                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      selectedVersionId === version.id
                        ? 'bg-purple-100 text-purple-800 border-purple-300'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border-gray-300'
                    } border`}
                  >
                    v{version.version_number}.0
                    {version === versions[0] && (
                      <span className="ml-1 text-xs">(Latest)</span>
                    )}
                  </button>
                ))}
              </div>
              {selectedVersion?.change_notes && (
                <div className="mt-2 text-sm text-gray-600 italic">
                  "{selectedVersion.change_notes}"
                </div>
              )}
            </div>
          )}

          <form onSubmit={(e) => { e.preventDefault(); handleSaveClick(); }} className="space-y-6">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Title *
              </label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Enter prompt title..."
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Description
              </label>
              <Input
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe what this prompt does..."
              />
            </div>

            {/* Content */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Prompt Content * (v{currentVersionNumber}.0)
              </label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                placeholder="Enter your prompt content here..."
                className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Tags
              </label>
              <div className="space-y-2">
                <div className="flex gap-2">
                  <Input
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    placeholder="Add a tag..."
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                    className="flex-1"
                  />
                  <Button type="button" onClick={addTag} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>

                {formData.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {formData.tags.map(tag => (
                      <span
                        key={tag}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                      >
                        <Tag className="h-3 w-3" />
                        {tag}
                        <button
                          type="button"
                          onClick={() => removeTag(tag)}
                          className="ml-1 text-blue-600 hover:text-blue-800"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center pt-4 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowTester(true)}
                disabled={!formData.content.trim()}
              >
                <Zap className="h-4 w-4 mr-2" />
                Test with LLMs
              </Button>
              <div className="flex gap-3">
                <Button type="button" variant="outline" onClick={onCancel}>
                  Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Save Confirmation Dialog */}
      {showSaveDialog && (
        <SaveConfirmDialog
          currentVersion={currentVersionNumber}
          onConfirm={handleConfirmSave}
          onCancel={() => setShowSaveDialog(false)}
        />
      )}
    </>
  );
};
