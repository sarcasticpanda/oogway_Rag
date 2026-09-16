import { useRef, useState } from 'react';
import { Database, Upload, RefreshCw, Layers, Trash2, Eye, Plus, Search, X } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

const API = '/api/v1';

interface Episode {
  id: string;
  title: string;
  guest_name: string;
  summary: string;
  created_at: string;
  expertise_tags: string[];
  key_frameworks: string[];
  chunk_count?: number;
}

export default function KnowledgeBasePage() {
  const [isIngesting, setIsIngesting] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [knowledgeMenuOpen, setKnowledgeMenuOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: episodes = [], isLoading, refetch } = useQuery<Episode[]>({
    queryKey: ['episodes'],
    queryFn: async () => {
      const res = await fetch(`${API}/knowledge/episodes`);
      if (!res.ok) throw new Error('Failed to fetch episodes');
      return res.json();
    },
    refetchInterval: 5000, // Auto-refresh every 5 seconds
    refetchOnWindowFocus: true,
  });

  const handleIngest = async () => {
    setIsIngesting(true);
    try {
      const res = await fetch(`${API}/knowledge/ingest`, { method: 'POST' });
      if (!res.ok) {
        throw new Error('Ingestion failed to start');
      }
      // Poll for new episodes every 3 seconds for 2 minutes
      const pollInterval = setInterval(() => refetch(), 3000);
      setTimeout(() => {
        clearInterval(pollInterval);
        setIsIngesting(false);
      }, 120000); // Stop polling after 2 minutes
    } catch (error) {
      console.error('Ingestion error:', error);
      alert('Failed to start ingestion. Check console for details.');
      setIsIngesting(false);
    }
  };

  const handleUpload = async (file?: File) => {
    if (!file) return;
    setIsUploading(true);
    setUploadMessage(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API}/knowledge/upload`, { method: 'POST', body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      setUploadMessage(data.message);
      await refetch();
    } catch (error) {
      setUploadMessage(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const deleteSource = async (id: string) => {
    if (!confirm('Delete this knowledge source and its indexed chunks?')) return;
    const response = await fetch(`${API}/knowledge/episodes/${id}`, { method: 'DELETE' });
    if (response.ok) await refetch();
  };

  const filteredEpisodes = episodes.filter((episode) =>
    `${episode.title} ${episode.guest_name} ${episode.summary}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="h-12 border-b border-border flex items-center justify-between px-6 bg-card shrink-0">
        <div className="flex items-center gap-2">
          <Database size={18} />
          <h1 className="text-sm font-semibold">Knowledge Base</h1>
          <span className="text-xs text-muted-foreground">({episodes.length} episodes)</span>
        </div>
        <div className="relative">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.pdf,.docx"
            className="hidden"
            onChange={(event) => handleUpload(event.target.files?.[0])}
          />
          <button
            onClick={() => setKnowledgeMenuOpen((open) => !open)}
            className="flex items-center gap-1.5 text-xs bg-primary text-primary-foreground px-3 py-1.5 rounded-lg disabled:opacity-50"
          >
            <Plus size={14} /> Add knowledge
          </button>
          {knowledgeMenuOpen && (
            <div className="absolute right-0 top-9 z-20 w-60 rounded-lg border border-border bg-card p-1 shadow-lg">
              <button onClick={() => { setKnowledgeMenuOpen(false); handleIngest(); }} className="w-full rounded-md px-3 py-2 text-left text-xs hover:bg-accent">
                Ingest bundled Lenny transcripts
              </button>
              <button onClick={() => { setKnowledgeMenuOpen(false); fileInputRef.current?.click(); }} className="w-full rounded-md px-3 py-2 text-left text-xs hover:bg-accent">
                Upload TXT, Markdown, PDF, or DOCX
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto">
          {/* Status Banner */}
          <div className="bg-secondary border border-border rounded-xl p-4 flex items-start gap-4 mb-6">
            <div className="bg-primary/20 p-2 rounded-full mt-1">
              <Layers size={20} className="text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground text-sm">RAG System Status</h3>
              <p className="text-xs text-muted-foreground mt-1">
                Lenny Growth Assistant uses Retrieval-Augmented Generation (RAG) to ground answers in these transcripts. 
                When you ask a question, the AI searches this vector database for relevant episode chunks and explicitly cites its sources.
              </p>
            </div>
          </div>
          {uploadMessage && (
            <div className="mb-6 rounded-lg border border-border bg-card px-4 py-3 text-xs text-foreground">
              {uploadMessage}
            </div>
          )}

          <div className="mb-5 flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2">
            <Search size={14} className="text-muted-foreground" />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search knowledge sources..." className="w-full bg-transparent text-xs outline-none" />
            <span className="text-[10px] text-muted-foreground">{filteredEpisodes.length} shown</span>
          </div>

          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground text-sm flex items-center justify-center gap-2">
              <RefreshCw size={16} className="animate-spin" /> Loading episodes...
            </div>
          ) : episodes.length === 0 ? (
            <div className="text-center py-20 border border-dashed border-border rounded-xl">
              <Database size={32} className="mx-auto text-muted-foreground/30 mb-3" />
              <h2 className="text-sm font-semibold text-foreground mb-1">Vector Database Empty</h2>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto mb-4">
                No transcripts have been ingested yet. The AI cannot ground its answers until data is available.
              </p>
              <button
                onClick={handleIngest}
                className="bg-primary text-primary-foreground text-xs px-4 py-2 rounded-lg font-medium"
              >
                Start Ingestion
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredEpisodes.map(ep => (
                <div key={ep.id} className="bg-card border border-border rounded-xl p-4 hover:border-primary/50 transition-colors">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-foreground text-sm mb-1">{ep.title}</h3>
                    <div className="flex items-center gap-1">
                      <button title="Open source" onClick={() => setSelectedEpisode(ep)} className="p-1 text-muted-foreground hover:text-foreground"><Eye size={14} /></button>
                      <button title="Delete source" onClick={() => deleteSource(ep.id)} className="p-1 text-muted-foreground hover:text-destructive"><Trash2 size={14} /></button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {ep.expertise_tags?.map((tag: string) => (
                      <span key={tag} className="text-[10px] bg-secondary text-muted-foreground px-2 py-0.5 rounded-full">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-3 mb-4">
                    {ep.summary}
                  </p>
                  <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-3 border-t border-border">
                    <span>{new Date(ep.created_at).toLocaleDateString()}</span>
                    <span className="font-medium text-primary">{ep.chunk_count ?? 0} chunks indexed</span>
                  </div>
                </div>
              ))}
            </div>
          )}
          {selectedEpisode && (
            <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 p-4" onClick={() => setSelectedEpisode(null)}>
              <div className="w-full max-w-lg rounded-xl border border-border bg-card p-5 shadow-xl" onClick={(event) => event.stopPropagation()}>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-base font-semibold">{selectedEpisode.title}</h2>
                    <p className="mt-1 text-xs text-muted-foreground">{selectedEpisode.guest_name}</p>
                  </div>
                  <button onClick={() => setSelectedEpisode(null)} className="p-1 text-muted-foreground hover:text-foreground"><X size={16} /></button>
                </div>
                <p className="mt-4 text-sm leading-6 text-muted-foreground">{selectedEpisode.summary || 'No summary available.'}</p>
                <div className="mt-5 flex items-center justify-between border-t border-border pt-3 text-xs">
                  <span>{selectedEpisode.chunk_count ?? 0} indexed chunks</span>
                  <span>{new Date(selectedEpisode.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
