import React, { useState, useEffect } from 'react';
import { Search, Plus, Tag, Clock, Edit, Trash2 } from 'lucide-react';
import { promptsApi, Prompt } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface PromptListProps {
  onSelectPrompt: (prompt: Prompt) => void;
  onEditPrompt: (prompt: Prompt) => void;
  onCreatePrompt: () => void;
}

export const PromptList: React.FC<PromptListProps> = ({
  onSelectPrompt,
  onEditPrompt,
  onCreatePrompt,
}) => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  useEffect(() => {
    loadPrompts();
  }, [searchTerm, selectedTags]);

  const loadPrompts = async () => {
    try {
      setLoading(true);
      const response = await promptsApi.getPrompts({
        search: searchTerm || undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
      });
      setPrompts(response.items || []);
    } catch (error) {
      console.error('Failed to load prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePrompt = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      try {
        await promptsApi.deletePrompt(id);
        setPrompts(prompts.filter(p => p.id !== id));
      } catch (error) {
        console.error('Failed to delete prompt:', error);
      }
    }
  };

  const getAllTags = () => {
    const tags = new Set<string>();
    prompts.forEach(prompt => {
      prompt.tags.forEach(tag => tags.add(tag));
    });
    return Array.from(tags);
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
        <h2 className="text-2xl font-bold">Prompts</h2>
        <Button onClick={onCreatePrompt} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Prompt
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search prompts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Tag Filters */}
        {getAllTags().length > 0 && (
          <div className="flex flex-wrap gap-2">
            {getAllTags().map(tag => (
              <button
                key={tag}
                onClick={() => {
                  setSelectedTags(prev =>
                    prev.includes(tag)
                      ? prev.filter(t => t !== tag)
                      : [...prev, tag]
                  );
                }}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  selectedTags.includes(tag)
                    ? 'bg-blue-100 text-blue-800 border-blue-200'
                    : 'bg-gray-100 text-gray-600 border-gray-200'
                } border`}
              >
                <Tag className="h-3 w-3 inline mr-1" />
                {tag}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Prompts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {prompts.map(prompt => (
          <Card key={prompt.id} className="hover:shadow-md transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div 
                  className="flex-1"
                  onClick={() => onSelectPrompt(prompt)}
                >
                  <CardTitle className="text-lg">{prompt.title}</CardTitle>
                  <CardDescription className="mt-2">
                    {prompt.description}
                  </CardDescription>
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onEditPrompt(prompt);
                    }}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeletePrompt(prompt.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent onClick={() => onSelectPrompt(prompt)}>
              <div className="space-y-3">
                {/* Tags */}
                {prompt.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {prompt.tags.map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Content Preview */}
                <div className="text-sm text-gray-600 line-clamp-3">
                  {prompt.content}
                </div>

                {/* Timestamp */}
                <div className="flex items-center text-xs text-gray-400">
                  <Clock className="h-3 w-3 mr-1" />
                  Updated {new Date(prompt.updated_at).toLocaleDateString()}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {prompts.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Search className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No prompts found
          </h3>
          <p className="text-gray-500 mb-4">
            {searchTerm || selectedTags.length > 0
              ? 'Try adjusting your search or filters'
              : 'Get started by creating your first prompt'}
          </p>
          {!searchTerm && selectedTags.length === 0 && (
            <Button onClick={onCreatePrompt}>
              <Plus className="h-4 w-4 mr-2" />
              Create Prompt
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
