import React, { useState } from 'react';
import { PromptList } from '@/components/prompts/PromptList';
import { PromptEditor } from '@/components/prompts/PromptEditor';
import { VersionedPromptEditor } from '@/components/prompts/VersionedPromptEditor';
import { VersionManager } from '@/components/versions/VersionManager';
import { ComparisonDashboard } from '@/components/comparisons/ComparisonDashboard';
import { NewComparisonForm } from '@/components/comparisons/NewComparisonForm';
import { LLMSettings } from '@/components/settings/LLMSettings';
import { Prompt } from '@/lib/api';

type View = 'prompts' | 'editor' | 'versions' | 'comparisons' | 'new-comparison' | 'settings';

function App() {
  const [currentView, setCurrentView] = useState<View>('prompts');
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | undefined>();

  const handleSelectPrompt = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    setCurrentView('versions');
  };

  const handleEditPrompt = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    setCurrentView('editor');
  };

  const handleCreatePrompt = () => {
    setSelectedPrompt(undefined);
    setCurrentView('editor');
  };

  const handleSavePrompt = () => {
    setSelectedPrompt(undefined);
    setCurrentView('prompts');
  };

  const handleCancelEditor = () => {
    setSelectedPrompt(undefined);
    setCurrentView('prompts');
  };

  const handleBackToPrompts = () => {
    setSelectedPrompt(undefined);
    setCurrentView('prompts');
  };

  const handleNewComparison = () => {
    setCurrentView('new-comparison');
  };

  const handleComparisonCreated = () => {
    setCurrentView('comparisons');
  };

  const handleCancelComparison = () => {
    setCurrentView('comparisons');
  };

  const renderView = () => {
    switch (currentView) {
      case 'prompts':
        return (
          <PromptList
            onSelectPrompt={handleSelectPrompt}
            onEditPrompt={handleEditPrompt}
            onCreatePrompt={handleCreatePrompt}
          />
        );

      case 'editor':
        return selectedPrompt ? (
          <VersionedPromptEditor
            prompt={selectedPrompt}
            onSave={handleSavePrompt}
            onCancel={handleCancelEditor}
          />
        ) : (
          <PromptEditor
            onSave={handleSavePrompt}
            onCancel={handleCancelEditor}
          />
        );

      case 'versions':
        return selectedPrompt ? (
          <VersionManager
            prompt={selectedPrompt}
            onBack={handleBackToPrompts}
          />
        ) : null;

      case 'comparisons':
        return (
          <ComparisonDashboard
            onNewComparison={handleNewComparison}
            onViewComparison={(comparison) => {
              // TODO: Implement comparison details view
              console.log('View comparison:', comparison);
            }}
          />
        );

      case 'new-comparison':
        return (
          <NewComparisonForm
            onCancel={handleCancelComparison}
            onCreated={handleComparisonCreated}
          />
        );

      case 'settings':
        return <LLMSettings />;

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Prompt Center</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentView('prompts')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'prompts'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Prompts
              </button>
              <button
                onClick={() => setCurrentView('comparisons')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'comparisons'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Comparisons
              </button>
              <button
                onClick={() => setCurrentView('settings')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'settings'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Settings
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderView()}
      </main>
    </div>
  );
}

export default App;
