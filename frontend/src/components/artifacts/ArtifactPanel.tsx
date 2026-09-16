import { useState } from 'react';
import { X, Copy, Download, Check, Code, Eye } from 'lucide-react';
import MarkdownRenderer from '../common/MarkdownRenderer';

interface ArtifactPanelProps {
  artifact: {
    id: string;
    title: string;
    type: string;
    artifact_type?: string;
    content: string;
    word_count?: number;
  };
  onClose: () => void;
}

export default function ArtifactPanel({ artifact, onClose }: ArtifactPanelProps) {
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview');
  const artifactType = artifact.type || artifact.artifact_type || 'markdown';

  const copyContent = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadContent = () => {
    const ext = artifactType === 'html' ? '.html' : '.md';
    const blob = new Blob([artifact.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_')}${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full flex flex-col bg-card border-l border-border">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border shrink-0">
        <div>
          <h2 className="font-semibold text-foreground text-sm">{artifact.title}</h2>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
            <span className="bg-primary/10 text-primary px-2 py-0.5 rounded-full font-medium uppercase">
              {artifactType}
            </span>
            {artifact.word_count && <span>{artifact.word_count} words</span>}
          </div>
        </div>
        <div className="flex items-center gap-1">
          {artifactType === 'markdown' && (
            <div className="flex items-center gap-0.5 bg-secondary rounded-lg p-0.5">
              <button
                onClick={() => setViewMode('preview')}
                className={`p-1.5 rounded ${viewMode === 'preview' ? 'bg-background' : 'hover:bg-background/50'} transition-colors`}
                title="Preview"
              >
                <Eye size={14} />
              </button>
              <button
                onClick={() => setViewMode('code')}
                className={`p-1.5 rounded ${viewMode === 'code' ? 'bg-background' : 'hover:bg-background/50'} transition-colors`}
                title="Code"
              >
                <Code size={14} />
              </button>
            </div>
          )}
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
        {artifactType === 'html' ? (
          <iframe
            sandbox="allow-scripts"
            srcDoc={artifact.content}
            className="w-full h-full min-h-[600px] border border-border rounded-lg bg-white"
            title={artifact.title}
          />
        ) : viewMode === 'preview' ? (
          <MarkdownRenderer content={artifact.content} />
        ) : (
          <pre className="text-xs bg-secondary p-4 rounded-lg overflow-x-auto font-mono">
            <code>{artifact.content}</code>
          </pre>
        )}
      </div>
    </div>
  );
}
