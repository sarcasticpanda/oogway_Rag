import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Cpu, Loader2, Copy, Check, RotateCcw, AlertTriangle, BookOpen, ChevronDown, ChevronUp, Box, Upload, Maximize2, Minimize2 } from 'lucide-react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { AppConfig } from '../../App';
import ArtifactPanel from '../artifacts/ArtifactPanel';
import MarkdownRenderer from '../common/MarkdownRenderer';

const API = '/api/v1';
const PROVIDERS = ['groq', 'gemini', 'openrouter', 'openai', 'anthropic', 'ollama', 'custom'];

interface Citation {
  episode_title?: string;
  guest?: string;
  chunk_text?: string;
  score?: number;
}

interface Message {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
  citations?: Citation[];
  is_grounded?: boolean;
  follow_ups?: string[];
  provider?: string;
  model?: string;
  artifactId?: string;
}

interface ChatAreaProps {
  sessionId: string | null;
  onSessionCreated: (id: string) => void;
  config: AppConfig;
  onConfigChange: (c: AppConfig) => void;
}

function MessageBubble({ msg, onFollowUp, onOpenArtifact }: { msg: Message; onFollowUp?: (q: string) => void; onOpenArtifact?: (id: string) => void }) {
  const [copied, setCopied] = useState(false);
  const [citationsOpen, setCitationsOpen] = useState(false);

  const copyText = () => {
    navigator.clipboard.writeText(msg.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const time = msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

  if (msg.role === 'user') {
    return (
      <div className="flex justify-end gap-3 max-w-4xl mx-auto w-full">
        <div className="max-w-[75%]">
          <div className="bg-primary text-primary-foreground px-4 py-3 rounded-2xl rounded-tr-sm whitespace-pre-wrap text-sm">
            {msg.content}
          </div>
          {time && <div className="text-[10px] text-muted-foreground text-right mt-1">{time}</div>}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start gap-3 max-w-4xl mx-auto w-full">
      <div className="max-w-[85%] space-y-2">
        {/* Model badge */}
        {msg.provider && (
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <Cpu size={10} />
            <span className="font-medium">{msg.provider}{msg.model ? `:${msg.model}` : ''}</span>
          </div>
        )}

        {/* Grounding warning */}
        {msg.is_grounded === false && (
          <div className="flex items-center gap-1.5 text-xs text-amber-500 bg-amber-500/10 px-2.5 py-1.5 rounded-lg">
            <AlertTriangle size={12} />
            <span>This answer may not be fully supported by Lenny's transcripts.</span>
          </div>
        )}

        {/* Content with markdown support */}
        <div className="bg-muted px-4 py-3 rounded-2xl rounded-tl-sm text-sm text-foreground">
          <MarkdownRenderer content={msg.content} className="" />
        </div>

        {/* Actions row */}
        <div className="flex items-center gap-2">
          <button onClick={copyText} className="p-1 text-muted-foreground hover:text-foreground transition-colors" title="Copy">
            {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
          </button>
          {time && <span className="text-[10px] text-muted-foreground">{time}</span>}
          {msg.artifactId && (
            <button onClick={() => onOpenArtifact?.(msg.artifactId!)} className="flex items-center gap-1 rounded-md bg-primary/10 px-2 py-1 text-xs text-primary hover:bg-primary/20">
              <Box size={12} /> Open artifact
            </button>
          )}

          {/* Citations toggle */}
          {msg.citations && msg.citations.length > 0 && (
            <button onClick={() => setCitationsOpen(!citationsOpen)}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors ml-2">
              <BookOpen size={12} />
              {msg.citations.length} source{msg.citations.length > 1 ? 's' : ''}
              {citationsOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
          )}
        </div>

        {/* Citations detail */}
        {citationsOpen && msg.citations && (
          <div className="space-y-1.5 pl-2 border-l-2 border-primary/20">
            {msg.citations.map((c, i) => (
              <div key={i} className="bg-background/50 border border-border rounded-lg px-3 py-2 text-xs">
                <div className="font-medium text-foreground">{c.episode_title || 'Unknown Episode'}</div>
                {c.guest && <div className="text-muted-foreground">Guest: {c.guest}</div>}
                {c.chunk_text && <div className="text-muted-foreground mt-1 line-clamp-3 italic">"{c.chunk_text}"</div>}
              </div>
            ))}
          </div>
        )}

        {/* Follow-up questions */}
        {msg.follow_ups && msg.follow_ups.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-1">
            {msg.follow_ups.map((q, i) => (
              <button key={i} onClick={() => onFollowUp?.(q)}
                className="text-xs bg-secondary hover:bg-accent border border-border px-3 py-1.5 rounded-full transition-colors text-foreground">
                {q}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatArea({ sessionId, onSessionCreated, config, onConfigChange }: ChatAreaProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentArtifact, setCurrentArtifact] = useState<any>(null);
  const [artifactRailOpen, setArtifactRailOpen] = useState(true);
  const [artifactExpanded, setArtifactExpanded] = useState(false);
  const [artifactMenuOpen, setArtifactMenuOpen] = useState(false);
  const [sourceSearch, setSourceSearch] = useState('');
  const [selectedSourceIds, setSelectedSourceIds] = useState<string[]>([]);
  const [sourceScope, setSourceScope] = useState<'all' | 'selected' | 'chat'>('all');
  const [sourcePickerOpen, setSourcePickerOpen] = useState(false);
  const uploadInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // Load session messages
  useQuery({
    queryKey: ['session-messages', sessionId],
    queryFn: async () => {
      if (!sessionId) { setMessages([]); return null; }
      const res = await fetch(`${API}/sessions/${sessionId}`);
      if (!res.ok) { setMessages([]); return null; }
      const data = await res.json();
      let artifactIndex = 0;
      setMessages(data.messages.map((m: any) => ({
        id: m.id,
        role: m.role,
        content: m.content || (m.message_type === 'artifact' ? 'Artifact created in this chat. Open it below.' : ''),
        created_at: m.created_at,
        citations: m.citations || [],
        artifactId: m.message_type === 'artifact' ? data.artifacts?.[artifactIndex++]?.id : undefined,
      })));
      return data;
    },
  });

  const { data: chatArtifacts = [] } = useQuery<any[]>({
    queryKey: ['chat-artifacts', sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const response = await fetch(`${API}/artifacts?session_id=${sessionId}`);
      return response.ok ? response.json() : [];
    },
    enabled: Boolean(sessionId),
  });

  const { data: knowledgeSources = [] } = useQuery<any[]>({
    queryKey: ['episodes'],
    queryFn: async () => {
      const response = await fetch(`${API}/knowledge/episodes`);
      return response.ok ? response.json() : [];
    },
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;
    setError(null);
    const userMsg: Message = { role: 'user', content: text, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    const isArtifactTask = /@(artifact|ship30)\b/i.test(text);

    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
          provider: config.provider,
          model: config.model || undefined,
          api_key: config.apiKey || undefined,
          base_url: config.customProviderUrl || undefined,
          user_preferences: (config.responseStyle || config.responseInstructions) ? { response_style: config.responseStyle, instructions: config.responseInstructions } : undefined,
          source_ids: selectedSourceIds.length ? selectedSourceIds : undefined,
          source_scope: isArtifactTask ? sourceScope : (selectedSourceIds.length ? 'selected' : 'all'),
          task_type: isArtifactTask ? 'artifact' : 'qa',
        }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();

      if (data.session_id && !sessionId) {
        onSessionCreated(data.session_id);
      }

      // Handle artifact if present
      if (data.artifact_data) {
        setArtifactRailOpen(true);
        setCurrentArtifact({
          id: data.artifact_id || 'temp-' + Date.now(),
          title: data.artifact_data.title,
          type: data.artifact_data.type,
          content: data.artifact_data.content,
          word_count: data.artifact_data.content.split(/\s+/).length
        });
      }

      const assistantMsg: Message = {
        role: 'assistant',
        content: data.message,
        created_at: new Date().toISOString(),
        citations: data.citations || [],
        is_grounded: data.is_grounded,
        follow_ups: data.follow_ups || [],
        provider: data.provider,
        model: data.model,
        artifactId: data.artifact_id || undefined,
      };
      setMessages(prev => [...prev, assistantMsg]);
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      queryClient.invalidateQueries({ queryKey: ['chat-artifacts', data.session_id] });
      queryClient.invalidateQueries({ queryKey: ['artifacts'] });
    } catch (err: any) {
      setError(err.message || 'Failed to get response');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, config, isLoading, onSessionCreated, queryClient]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleChatUpload = async (file?: File) => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setError(null);
    try {
      const response = await fetch(`${API}/knowledge/upload`, { method: 'POST', body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Upload failed');
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
      setMessages((previous) => [...previous, { role: 'assistant', content: `Knowledge source added and indexed: ${data.message}`, created_at: new Date().toISOString() }]);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : 'Upload failed');
    } finally {
      if (uploadInputRef.current) uploadInputRef.current.value = '';
    }
  };

  return (
    <div className="relative flex h-full">
      <div className="flex flex-col h-full flex-1 min-w-0">
      {/* Top bar */}
      <div className="h-12 border-b border-border flex items-center justify-between px-4 bg-card shrink-0">
        <h2 className="text-sm font-semibold text-foreground truncate">Lenny Growth Assistant</h2>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-secondary px-2.5 py-1 rounded-lg text-xs">
            <Cpu size={13} className="text-muted-foreground" />
            <select value={config.provider} onChange={(e) => onConfigChange({ ...config, provider: e.target.value })}
              className="bg-transparent outline-none cursor-pointer font-medium text-foreground">
              {PROVIDERS.map(p => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
            </select>
          </div>
          <input type="text" placeholder="Model" value={config.model}
            onChange={(e) => onConfigChange({ ...config, model: e.target.value })}
            className="bg-secondary px-2.5 py-1 rounded-lg text-xs outline-none w-28 text-foreground placeholder:text-muted-foreground" />
          <div className="relative hidden md:block">
            <button type="button" onClick={() => setSourcePickerOpen((open) => !open)} className="cursor-pointer rounded-lg bg-secondary px-2.5 py-1 text-[10px] text-foreground">
              Sources: {selectedSourceIds.length ? `${selectedSourceIds.length} selected` : 'All'}
            </button>
            {sourcePickerOpen && (
              <div className="absolute right-0 top-8 z-30 max-h-96 w-80 overflow-y-auto rounded-lg border border-border bg-card p-2 shadow-xl">
              <input value={sourceSearch} onChange={(event) => setSourceSearch(event.target.value)} placeholder="Search documents..." className="mb-2 w-full rounded border border-border bg-secondary px-2 py-1.5 text-xs outline-none" />
                <div className="mb-2 grid grid-cols-3 gap-1 border-b border-border pb-2">
                  {([['all', 'All knowledge'], ['selected', 'Selected docs'], ['chat', 'This chat']] as const).map(([scope, label]) => (
                    <button key={scope} type="button" onClick={() => setSourceScope(scope)} className={`rounded px-1 py-1 text-[10px] ${sourceScope === scope ? 'bg-primary text-primary-foreground' : 'bg-secondary hover:bg-accent'}`}>{label}</button>
                  ))}
                </div>
              <label className="flex items-center gap-2 border-b border-border px-2 py-2 text-xs font-medium">
                <input type="checkbox" checked={sourceScope === 'all' && selectedSourceIds.length === 0} onChange={() => { setSelectedSourceIds([]); setSourceScope('all'); setSourcePickerOpen(false); }} />
                Search all sources
              </label>
              {knowledgeSources.filter((source: any) => source.title.toLowerCase().includes(sourceSearch.toLowerCase())).map((source: any) => (
                <label key={source.id} className="flex items-start gap-2 rounded px-2 py-1.5 text-[10px] hover:bg-accent">
                  <input
                    type="checkbox"
                    checked={selectedSourceIds.includes(source.id)}
                    onChange={(event) => {
                      setSourceScope(event.target.checked ? 'selected' : (selectedSourceIds.length > 1 ? 'selected' : 'all'));
                      setSelectedSourceIds((current) => event.target.checked ? [...current, source.id] : current.filter((id) => id !== source.id));
                    }}
                  />
                  <span className="line-clamp-2">{source.title}</span>
                </label>
              ))}
              <button type="button" onClick={() => setSourcePickerOpen(false)} className="mt-2 w-full rounded bg-primary px-2 py-1.5 text-[10px] text-primary-foreground">Done</button>
            </div>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-5">
        {messages.length === 0 && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <h1 className="text-2xl font-bold text-foreground mb-2">How can I help you grow?</h1>
            <p className="text-sm text-muted-foreground max-w-md">
              Ask about Lenny's podcast, growth strategies, product management, or generate a Ship 30 essay.
            </p>
          </div>
        ) : (
            messages.map((m, i) => (
            <MessageBubble key={i} msg={m} onFollowUp={(q) => sendMessage(q)} onOpenArtifact={async (id) => { const response = await fetch(`${API}/artifacts/${id}`); if (response.ok) { const record = await response.json(); setCurrentArtifact({ ...record, type: record.type || record.artifact_type }); setArtifactRailOpen(true); } }} />
          ))
        )}

        {isLoading && (
          <div className="flex gap-3 max-w-4xl mx-auto w-full">
            <div className="bg-muted px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-2 text-sm">
              <Loader2 className="animate-spin" size={16} />
              <span className="text-muted-foreground">Thinking...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="flex gap-3 max-w-4xl mx-auto w-full">
            <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-2xl text-sm flex items-center gap-2">
              <AlertTriangle size={16} />
              <span>{error}</span>
              <button onClick={() => { setError(null); sendMessage(messages[messages.length - 2]?.content || ''); }}
                className="ml-2 flex items-center gap-1 underline text-xs">
                <RotateCcw size={12} /> Retry
              </button>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border p-4 bg-card shrink-0">
        <div className="max-w-4xl mx-auto relative">
          
          {/* Mention Popover */}
          {(() => {
            const match = input.match(/@([a-z]*)$/i);
            const showMention = match !== null && "artifact".startsWith(match[1].toLowerCase());
            if (!showMention && !artifactMenuOpen) return null;
            return (
              <div className="absolute bottom-full left-4 mb-2 bg-card border border-border rounded-lg shadow-lg overflow-hidden z-10 min-w-[200px]">
                <button 
                  type="button"
                  onClick={() => {
                    setInput(input.replace(/@([a-z]*)$/i, '@artifact '));
                    setArtifactMenuOpen(true);
                  }}
                  className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-accent text-foreground w-full text-left"
                >
                  <Box size={14} className="text-primary" />
                  <span className="font-medium">artifact</span>
                  <span className="text-xs text-muted-foreground ml-auto">Ship 30 Essay</span>
                </button>
                {artifactMenuOpen && (
                  <div className="border-t border-border p-1">
                    <div className="px-3 pb-1 pt-2 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">Artifact type</div>
                    {[
                      ['ship30', 'Essay: 1,150-1,350 words'],
                      ['summary', 'Summary of this chat'],
                      ['report', 'Structured report'],
                      ['checklist', 'Action checklist'],
                      ['html', 'HTML/CSS webpage'],
                    ].map(([kind, label]) => (
                      <button key={kind} type="button" onClick={() => { setInput(`${input.replace(/@([a-z]*)\s*$/i, '@artifact ')}${kind}: `); }} className="block w-full rounded px-3 py-1.5 text-left text-xs hover:bg-accent">
                        {label}
                      </button>
                    ))}
                    <div className="mt-1 border-t border-border px-3 pb-1 pt-2 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">Use as reference</div>
                    <div className="grid grid-cols-3 gap-1 px-2 pb-2">
                      {([['all', 'All knowledge'], ['selected', 'Selected docs'], ['chat', 'This chat']] as const).map(([scope, label]) => (
                        <button key={scope} type="button" onClick={() => setSourceScope(scope)} className={`rounded px-1 py-1 text-[10px] ${sourceScope === scope ? 'bg-primary text-primary-foreground' : 'bg-secondary hover:bg-accent'}`}>
                          {label}
                        </button>
                      ))}
                    </div>
                    {sourceScope === 'selected' && (
                      <div className="max-h-40 overflow-y-auto border-t border-border px-2 pt-2">
                        <input value={sourceSearch} onChange={(event) => setSourceSearch(event.target.value)} placeholder="Search documents..." className="mb-2 w-full rounded border border-border bg-secondary px-2 py-1.5 text-xs outline-none" />
                        {knowledgeSources.filter((source: any) => source.title.toLowerCase().includes(sourceSearch.toLowerCase())).map((source: any) => (
                          <label key={source.id} className="flex items-start gap-2 rounded px-2 py-1.5 text-[10px] hover:bg-accent">
                            <input type="checkbox" checked={selectedSourceIds.includes(source.id)} onChange={(event) => { setSourceScope(event.target.checked ? 'selected' : sourceScope); setSelectedSourceIds((current) => event.target.checked ? [...current, source.id] : current.filter((id) => id !== source.id)); }} />
                            <span className="line-clamp-2">{source.title}</span>
                          </label>
                        ))}
                      </div>
                    )}
                    <div className="border-t border-border px-3 py-2 text-[10px] text-muted-foreground">
                      {sourceScope === 'selected' ? `${selectedSourceIds.length} document(s) selected` : sourceScope === 'chat' ? 'Uses this conversation' : 'Uses all indexed knowledge'}
                    </div>
                    <button type="button" onClick={() => setArtifactMenuOpen(false)} className="mx-2 mb-2 w-[calc(100%-1rem)] rounded bg-primary px-2 py-1.5 text-[10px] text-primary-foreground">Done</button>
                  </div>
                )}
              </div>
            );
          })()}

          <form onSubmit={handleSubmit} className="relative">
            <input ref={uploadInputRef} type="file" accept=".txt,.md,.pdf,.docx" className="hidden" onChange={(event) => handleChatUpload(event.target.files?.[0])} />
            <textarea value={input} onChange={(e) => setInput(e.target.value)}
              placeholder="Message Lenny... (Type @ to generate an artifact)" rows={1}
              className="w-full bg-secondary rounded-xl py-3 pl-4 pr-12 resize-none outline-none text-sm text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/20"
              onKeyDown={(e) => { 
                if (e.key === 'Enter' && !e.shiftKey) { 
                  e.preventDefault(); 
                  const match = input.match(/@([a-z]*)$/i);
                  const showMention = match !== null && "artifact".startsWith(match[1].toLowerCase());
                  if (showMention) {
                    setInput(input.replace(/@([a-z]*)$/i, '@artifact '));
                  } else {
                    handleSubmit(e); 
                  }
                } 
              }} />
            <button type="submit" disabled={!input.trim() || isLoading}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-primary text-primary-foreground rounded-lg disabled:opacity-40 transition-opacity">
              <Send size={16} />
            </button>
            <button type="button" title="Add transcript or document" onClick={() => uploadInputRef.current?.click()} className="absolute right-12 top-1/2 -translate-y-1/2 p-2 text-muted-foreground hover:text-foreground">
              <Upload size={15} />
            </button>
          </form>
          <div className="text-center mt-1.5 text-[10px] text-muted-foreground">
            Responses are grounded in Lenny's Podcast transcripts. Verify important information.
          </div>
        </div>
      </div>
      </div>

      {chatArtifacts.length > 0 && !artifactRailOpen && (
        <button onClick={() => setArtifactRailOpen(true)} className="absolute right-3 top-16 z-20 rounded-l-lg border border-border bg-card px-2 py-3 text-xs shadow-lg" title="Show artifacts">
          <Box size={15} />
        </button>
      )}

      {chatArtifacts.length > 0 && artifactRailOpen && (
        <div className={`absolute z-20 flex flex-col overflow-hidden rounded-xl border border-border bg-card shadow-2xl ${artifactExpanded ? 'inset-3' : 'inset-y-3 right-3 w-[min(46vw,680px)] min-w-[340px]'}`}>
          <div className="flex items-center justify-between border-b border-border px-3 py-2">
            <span className="text-xs font-semibold">Artifacts in this chat</span>
            <div className="flex items-center gap-1">
              <button onClick={() => setArtifactExpanded((expanded) => !expanded)} className="rounded p-1 text-muted-foreground hover:bg-accent" title={artifactExpanded ? 'Use medium view' : 'Expand artifact'}>
                {artifactExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
              </button>
              <button onClick={() => setArtifactRailOpen(false)} className="rounded p-1 text-muted-foreground hover:bg-accent" title="Collapse artifacts"><ChevronDown size={15} /></button>
            </div>
          </div>
          <div className="flex gap-1 overflow-x-auto border-b border-border p-2">
            {chatArtifacts.map((artifact: any) => (
              <button key={artifact.id} onClick={async () => { const response = await fetch(`${API}/artifacts/${artifact.id}`); if (response.ok) { const record = await response.json(); setCurrentArtifact({ ...record, type: record.type || record.artifact_type }); } }} className={`shrink-0 rounded border px-2 py-1 text-left text-[10px] ${currentArtifact?.id === artifact.id ? 'border-primary bg-primary/10' : 'border-border hover:bg-accent'}`}>
                {artifact.title}
              </button>
            ))}
          </div>
          <div className="min-h-0 flex-1">
            {currentArtifact ? <ArtifactPanel artifact={currentArtifact} onClose={() => setCurrentArtifact(null)} /> : <div className="flex h-full items-center justify-center p-6 text-center text-xs text-muted-foreground">Select an artifact above to preview it here.</div>}
          </div>
        </div>
      )}
    </div>
  );
}
