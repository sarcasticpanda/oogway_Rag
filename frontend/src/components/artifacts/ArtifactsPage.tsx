import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Box, FileText, Code, Copy, Check, Download, RotateCcw, Trash2, BookOpen, ChevronDown, ChevronUp, X } from 'lucide-react';
import MarkdownRenderer from '../common/MarkdownRenderer';

const API = '/api/v1';

interface Artifact {
  id: string;
  title: string;
  artifact_type: string;
  content?: string;
  word_count?: number;
  created_at: string;
  session_id?: string;
  session_title?: string;
  source_references?: any[];
}

function ArtifactViewer({ artifact, onClose }: { artifact: Artifact; onClose: () => void }) {
  const [copied, setCopied] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(false);

  const copyContent = () => {
    navigator.clipboard.writeText(artifact.content || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadContent = () => {
    const ext = artifact.artifact_type === 'html' ? '.html' : '.md';
    const blob = new Blob([artifact.content || ''], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_')}${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border shrink-0">
          <div>
            <h2 className="font-semibold text-foreground">{artifact.title}</h2>
            <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
              <span className="bg-secondary px-2 py-0.5 rounded-full font-medium uppercase">{artifact.artifact_type}</span>
              {artifact.word_count && <span>{artifact.word_count} words</span>}
              <span>{new Date(artifact.created_at).toLocaleDateString()}</span>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button onClick={copyContent} className="p-2 hover:bg-accent rounded-md transition-colors" title="Copy">
              {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
            </button>
            <button onClick={downloadContent} className="p-2 hover:bg-accent rounded-md transition-colors" title="Download">
              <Download size={16} />
            </button>
            <button onClick={onClose} className="p-2 hover:bg-accent rounded-md transition-colors">
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {artifact.artifact_type === 'html' ? (
            /* Sandboxed HTML rendering — no allow-same-origin for security */
            <iframe
              sandbox="allow-scripts"
              srcDoc={artifact.content}
              className="w-full h-full min-h-[500px] border border-border rounded-lg bg-white"
              title={artifact.title}
            />
          ) : (
            <MarkdownRenderer content={artifact.content || ''} />
          )}
        </div>

        {/* Source references */}
        {artifact.source_references && artifact.source_references.length > 0 && (
          <div className="border-t border-border p-4 shrink-0">
            <button onClick={() => setSourcesOpen(!sourcesOpen)}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors">
              <BookOpen size={12} />
              {artifact.source_references.length} source{artifact.source_references.length > 1 ? 's' : ''}
              {sourcesOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
            {sourcesOpen && (
              <div className="mt-2 space-y-1">
                {artifact.source_references.map((ref: any, i: number) => (
                  <div key={i} className="text-xs bg-secondary rounded-lg px-3 py-2">
                    {ref.episode_title || ref.title || JSON.stringify(ref)}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ArtifactsPage() {
  const queryClient = useQueryClient();
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);

  const { data: artifacts = [], isLoading } = useQuery<Artifact[]>({
    queryKey: ['artifacts'],
    queryFn: async () => {
      const res = await fetch(`${API}/artifacts`);
      if (!res.ok) return [];
      return res.json();
    },
  });

  const artifactsByChat = artifacts.reduce<Record<string, Artifact[]>>((groups, artifact) => {
    const chat = artifact.session_title || artifact.session_id || 'Unassigned chat';
    (groups[chat] ||= []).push(artifact);
    return groups;
  }, {});

  const deleteArtifact = async (id: string) => {
    await fetch(`${API}/artifacts/${id}`, { method: 'DELETE' });
    queryClient.invalidateQueries({ queryKey: ['artifacts'] });
  };

  const openArtifact = async (a: Artifact) => {
    // Fetch full content if needed
    if (!a.content) {
      const res = await fetch(`${API}/artifacts/${a.id}`);
      if (res.ok) {
        const full = await res.json();
        setSelectedArtifact(full);
        return;
      }
    }
    setSelectedArtifact(a);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="h-12 border-b border-border flex items-center px-6 bg-card shrink-0">
        <Box size={18} className="mr-2" />
        <h1 className="text-sm font-semibold">Artifacts</h1>
        <span className="ml-2 text-xs text-muted-foreground">({artifacts.length})</span>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="text-center text-muted-foreground py-12">Loading artifacts...</div>
        ) : artifacts.length === 0 ? (
          <div className="text-center py-20">
            <Box size={48} className="mx-auto text-muted-foreground/30 mb-4" />
            <h2 className="text-lg font-semibold text-foreground mb-1">No artifacts yet</h2>
            <p className="text-sm text-muted-foreground max-w-sm mx-auto">
              Generate a Ship 30 essay or ask the assistant to create a report. Artifacts will appear here.
            </p>
          </div>
        ) : (
          <div className="max-w-6xl space-y-8">
            {Object.entries(artifactsByChat).map(([chat, chatArtifacts]) => (
              <section key={chat}>
                <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">{chat}</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {chatArtifacts.map(a => (
                    <div key={a.id} onClick={() => openArtifact(a)}
                      className="bg-card border border-border rounded-xl p-4 hover:border-primary/30 hover:shadow-md transition-all cursor-pointer group">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {a.artifact_type === 'html' ? <Code size={16} className="text-blue-500" /> : <FileText size={16} className="text-green-500" />}
                          <span className="text-[10px] bg-secondary px-2 py-0.5 rounded-full font-medium uppercase">{a.artifact_type}</span>
                        </div>
                        <button onClick={(e) => { e.stopPropagation(); deleteArtifact(a.id); }}
                          className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive transition-all">
                          <Trash2 size={14} />
                        </button>
                      </div>
                      <h3 className="font-medium text-sm text-foreground mb-1 line-clamp-2">{a.title}</h3>
                      <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                        {a.word_count && <span>{a.word_count} words</span>}
                        <span>{new Date(a.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            ))}
          </div>
        )}
      </div>

      {selectedArtifact && (
        <ArtifactViewer artifact={selectedArtifact} onClose={() => setSelectedArtifact(null)} />
      )}
    </div>
  );
}
