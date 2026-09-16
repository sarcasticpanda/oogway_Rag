import { Settings, Save, X, Cpu, Trash2, Archive, Key, Eye, EyeOff, Loader2 } from 'lucide-react';
import type { AppConfig } from '../../types/config';
import { PROVIDER_CONFIGS } from '../../types/config';
import { useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';

const PROVIDERS = ['groq', 'gemini', 'openrouter', 'openai', 'anthropic', 'ollama', 'custom'];

interface OllamaModel {
  name: string;
  size: number;
}

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  config: AppConfig;
  onConfigChange: (c: AppConfig) => void;
}

export default function SettingsModal({ isOpen, onClose, config, onConfigChange }: SettingsModalProps) {
  const [localConfig, setLocalConfig] = useState(config);
  const [showApiKey, setShowApiKey] = useState(false);
  const [ollamaModels, setOllamaModels] = useState<OllamaModel[]>([]);
  const [ollamaStatus, setOllamaStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const queryClient = useQueryClient();

  useEffect(() => setLocalConfig(config), [config]);

  // Fetch Ollama models when modal opens or provider changes to ollama
  useEffect(() => {
    if (isOpen && localConfig.provider === 'ollama') {
      fetchOllamaModels();
    }
  }, [isOpen, localConfig.provider]);

  const fetchOllamaModels = async () => {
    setOllamaStatus('checking');
    try {
      const resp = await fetch('/api/v1/models');
      const data = await resp.json();
      if (data.ollama?.status === 'online') {
        setOllamaStatus('online');
        // Fetch detailed model list from Ollama
        const ollamaUrl = data.ollama.endpoint || 'http://localhost:11434';
        const tagsResp = await fetch(`${ollamaUrl}/api/tags`);
        if (tagsResp.ok) {
          const tagsData = await tagsResp.json();
          setOllamaModels(tagsData.models || []);
        }
      } else {
        setOllamaStatus('offline');
        setOllamaModels([]);
      }
    } catch {
      setOllamaStatus('offline');
      setOllamaModels([]);
    }
  };

  if (!isOpen) return null;

  const handleSave = () => {
    onConfigChange(localConfig);
    onClose();
  };

  const handleClearAll = async () => {
    if (confirm('Are you sure you want to delete all chats? This cannot be undone.')) {
      await fetch('/api/v1/sessions', { method: 'DELETE' });
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      onClose();
    }
  };

  // Determine which model to show
  const resolvedModel = localConfig.model || 
    (localConfig.provider === 'ollama' ? 'llama3.1' : 
     PROVIDER_CONFIGS[localConfig.provider as keyof typeof PROVIDER_CONFIGS]?.models?.[0] || '');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-card w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden border border-border flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Settings size={18} className="text-foreground" />
            <h2 className="text-base font-semibold text-foreground">Settings</h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-secondary rounded-lg transition-colors text-muted-foreground">
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          
          {/* AI Provider Configuration */}
          <section className="space-y-3">
            <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
              <Cpu size={16} /> AI Provider Configuration
            </h3>
            <div className="space-y-3 pl-6">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Active Provider</label>
                <select
                  value={localConfig.provider}
                  onChange={(e) => setLocalConfig({ ...localConfig, provider: e.target.value })}
                  className="w-full bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50"
                >
                  {PROVIDERS.map(p => (
                    <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                  ))}
                </select>
              </div>

              {/* Ollama Model Selector */}
              {localConfig.provider === 'ollama' && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="block text-xs font-medium text-muted-foreground">
                      Local Ollama Model
                    </label>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs ${ollamaStatus === 'online' ? 'text-green-500' : ollamaStatus === 'offline' ? 'text-red-500' : 'text-yellow-500'}`}>
                        {ollamaStatus === 'online' ? '● Ollama Online' : 
                         ollamaStatus === 'offline' ? '● Ollama Offline' : '● Checking...'}
                      </span>
                      <button 
                        onClick={fetchOllamaModels}
                        className="p-1 hover:bg-secondary rounded transition-colors"
                        title="Refresh model list"
                      >
                        <Loader2 size={12} className={ollamaStatus === 'checking' ? 'animate-spin' : ''} />
                      </button>
                    </div>
                  </div>
                  
                  {ollamaStatus === 'online' && ollamaModels.length > 0 ? (
                    <select
                      value={localConfig.model || ollamaModels[0]?.name || ''}
                      onChange={(e) => setLocalConfig({ ...localConfig, model: e.target.value })}
                      className="w-full bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50"
                    >
                      {ollamaModels.map(model => (
                        <option key={model.name} value={model.name}>
                          {model.name} ({Math.round(model.size / 1e9)}GB)
                        </option>
                      ))}
                    </select>
                  ) : ollamaStatus === 'offline' ? (
                    <div className="text-xs text-muted-foreground p-3 bg-secondary/50 rounded-lg border border-border">
                      Ollama is not running. Please start Ollama to use local models.
                      <br /><br />
                      To start: <code className="bg-background px-1 rounded">ollama serve</code>
                    </div>
                  ) : (
                    <div className="text-xs text-muted-foreground p-3 bg-secondary/50 rounded-lg flex items-center gap-2">
                      <Loader2 size={12} className="animate-spin" />
                      Checking Ollama connection...
                    </div>
                  )}

                  {/* Manual model input */}
                  <input
                    type="text"
                    placeholder="Or enter custom model name (e.g., llama3.1:latest)"
                    value={localConfig.model || ''}
                    onChange={(e) => setLocalConfig({ ...localConfig, model: e.target.value })}
                    className="w-full bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50"
                  />
                </div>
              )}

              {/* Other providers model selector */}
              {localConfig.provider !== 'ollama' && localConfig.provider !== 'custom' && (
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Model</label>
                  <input
                    type="text"
                    value={localConfig.model || ''}
                    onChange={(e) => setLocalConfig({ ...localConfig, model: e.target.value })}
                    placeholder={`Default: ${PROVIDER_CONFIGS[localConfig.provider as keyof typeof PROVIDER_CONFIGS]?.models?.[0] || 'see docs'}`}
                    className="w-full bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Response style</label>
                <select 
                  value={localConfig.responseStyle || ''} 
                  onChange={(e) => setLocalConfig({ ...localConfig, responseStyle: e.target.value })} 
                  className="w-full bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none"
                >
                  <option value="">Default grounded advisor</option>
                  <option value="Concise and direct; prioritize short actionable bullets.">Concise and actionable</option>
                  <option value="Detailed and analytical; explain reasoning and tradeoffs.">Detailed and analytical</option>
                  <option value="Warm and coaching-oriented; use plain language and examples.">Coaching-oriented</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Personal response instructions</label>
                <textarea
                  value={localConfig.responseInstructions || ''}
                  onChange={(e) => setLocalConfig({ ...localConfig, responseInstructions: e.target.value })}
                  placeholder="Example: Be concise, challenge weak assumptions, and end with three practical next steps."
                  rows={3}
                  className="w-full resize-none bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50"
                />
                <p className="text-[10px] text-muted-foreground mt-1">Applied to future replies in this browser session.</p>
              </div>

              {/* API Key field — shown for providers that need one */}
              {localConfig.provider !== 'ollama' && (
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">
                    <Key size={12} className="inline mr-1" />
                    API Key ({localConfig.provider})
                  </label>
                  <div className="relative">
                    <input
                      type={showApiKey ? 'text' : 'password'}
                      placeholder={`Enter your ${localConfig.provider} API key`}
                      value={localConfig.apiKey || ''}
                      onChange={(e) => setLocalConfig({ ...localConfig, apiKey: e.target.value })}
                      className="w-full bg-secondary border border-border rounded-lg px-3 py-2 pr-10 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50"
                    />
                    <button 
                      type="button" 
                      onClick={() => setShowApiKey((visible) => !visible)} 
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground"
                      title={showApiKey ? 'Hide API key' : 'Show API key'}
                    >
                      {showApiKey ? <EyeOff size={15} /> : <Eye size={15} />}
                    </button>
                  </div>
                  <p className="text-[10px] text-muted-foreground mt-1">Stored in browser only. Sent to backend per request.</p>
                </div>
              )}

              {/* Custom URL field — shown for Ollama or Custom */}
              {(localConfig.provider === 'ollama' || localConfig.provider === 'custom') && (
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">
                    Provider URL
                  </label>
                  <input
                    type="text"
                    placeholder={localConfig.provider === 'ollama' ? 'http://localhost:11434' : 'http://your-server:8080/v1'}
                    value={localConfig.customProviderUrl || ''}
                    onChange={(e) => setLocalConfig({ ...localConfig, customProviderUrl: e.target.value })}
                    className="w-full bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50"
                  />
                  <p className="text-[10px] text-muted-foreground mt-1">Custom OpenAI-compatible endpoint URL</p>
                </div>
              )}
            </div>
          </section>

          <hr className="border-border" />

          {/* Chat Management */}
          <section className="space-y-3">
            <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
              <Archive size={16} /> Chat Management
            </h3>
            <div className="pl-6 space-y-2">
              <div className="p-3 bg-secondary/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-muted-foreground">
                    Delete all chat history. This action cannot be undone.
                  </p>
                </div>
                <button
                  onClick={handleClearAll}
                  className="flex items-center gap-2 px-3 py-1.5 bg-destructive/10 text-destructive rounded-md text-xs hover:bg-destructive/20 transition-colors"
                >
                  <Trash2 size={12} />
                  Clear All Chats
                </button>
              </div>
              
              <div className="p-3 bg-secondary/50 rounded-lg">
                <p className="text-xs text-muted-foreground">
                  To rename or export individual chats, use the chat list in the sidebar. Right-click on a session for more options.
                </p>
              </div>
            </div>
          </section>

          {/* About */}
          <section className="space-y-3">
            <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
              <Cpu size={16} /> About
            </h3>
            <div className="pl-6 text-xs text-muted-foreground space-y-1">
              <p><strong>Version:</strong> 1.0.0</p>
              <p><strong>Backend:</strong> FastAPI + PostgreSQL + pgvector</p>
              <p><strong>Frontend:</strong> React + Vite + Tailwind CSS</p>
              <p><strong>AI Providers:</strong> Groq, OpenAI, Anthropic, Ollama (local)</p>
              <p><strong>Embeddings:</strong> nomic-embed-text (768 dimensions)</p>
              <p><strong>Vector Index:</strong> HNSW for fast similarity search</p>
            </div>
          </section>

        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 p-4 border-t border-border bg-secondary/30">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            <Save size={14} />
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
