import { Settings, Save, X, Cpu, Trash2, Archive, Key, Eye, EyeOff } from 'lucide-react';
import type { AppConfig } from '../../types/config';
import { PROVIDER_CONFIGS } from '../../types/config';
import { useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';

const PROVIDERS = ['groq', 'gemini', 'openrouter', 'openai', 'anthropic', 'ollama', 'custom'];

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  config: AppConfig;
  onConfigChange: (c: AppConfig) => void;
}

export default function SettingsModal({ isOpen, onClose, config, onConfigChange }: SettingsModalProps) {
  const [localConfig, setLocalConfig] = useState(config);
  const [showApiKey, setShowApiKey] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => setLocalConfig(config), [config]);

  if (!isOpen) return null;

  const handleSave = () => {
    onConfigChange(localConfig);
    onClose();
  };

  const handleClearAll = async () => {
    if (confirm('Are you sure you want to delete all chats?')) {
      await fetch('/api/v1/sessions', { method: 'DELETE' });
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-card w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden border border-border flex flex-col">
        
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
        <div className="p-6 space-y-6 overflow-y-auto max-h-[70vh]">
          
          {/* Models */}
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

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Response style</label>
                <select value={localConfig.responseStyle || ''} onChange={(e) => setLocalConfig({ ...localConfig, responseStyle: e.target.value })} className="w-full bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none">
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
                    className="w-full bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50"
                  />
                  <button type="button" onClick={() => setShowApiKey((visible) => !visible)} className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground" title={showApiKey ? 'Hide API key' : 'Show API key'}>
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

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Model Override (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. gpt-4o, claude-3.5-sonnet, qwen2.5-coder:3b"
                  value={localConfig.model || ''}
                  onChange={(e) => setLocalConfig({ ...localConfig, model: e.target.value })}
                  className="w-full bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50"
                />
              </div>
            </div>
          </section>

          <hr className="border-border" />

          {/* Chat Management */}
          <section className="space-y-3">
            <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
              <Archive size={16} /> Chat Management
            </h3>
            <div className="pl-6 space-y-2">
              <button 
                onClick={handleClearAll}
                className="flex items-center gap-2 text-sm text-destructive hover:bg-destructive/10 px-3 py-2 rounded-lg transition-colors w-full text-left"
              >
                <Trash2 size={16} /> Clear all chats
              </button>
            </div>
          </section>

        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border flex justify-end gap-2 bg-secondary/30">
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm font-medium text-foreground hover:bg-secondary transition-colors">
            Cancel
          </button>
          <button onClick={handleSave} className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">
            <Save size={16} /> Save Changes
          </button>
        </div>

      </div>
    </div>
  );
}
