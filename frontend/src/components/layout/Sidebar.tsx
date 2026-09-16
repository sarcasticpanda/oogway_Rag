import { MessageSquarePlus, FileText, Box, Settings, ChevronLeft, ChevronRight, Trash2, Search, Database, User, MoreVertical, Pencil, Download, Copy, X } from 'lucide-react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import SettingsModal from '../settings/SettingsModal';
import type { AppConfig } from '../../App';

const API = '/api/v1';

interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  active_provider: string;
  active_model: string;
}

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  config: AppConfig;
  onConfigChange: (c: AppConfig) => void;
}

// Context menu for each session
function SessionContextMenu({ 
  session, 
  currentSessionId, 
  onSelectSession, 
  onDelete,
  onRename,
  onDuplicate,
  onExport,
  onClose 
}: { 
  session: Session;
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onDelete: (id: string) => void;
  onRename: (id: string, newTitle: string) => void;
  onDuplicate: (id: string) => void;
  onExport: (id: string) => void;
  onClose: () => void;
}) {
  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(session.title);

  const handleRenameSubmit = async () => {
    if (renameValue.trim() && renameValue !== session.title) {
      await onRename(session.id, renameValue.trim());
    }
    setIsRenaming(false);
  };

  return (
    <div className="relative">
      <button
        onClick={(e) => e.stopPropagation()}
        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-accent rounded transition-all"
        title="More options"
      >
        <MoreVertical size={12} />
      </button>
      
      {/* Context Menu */}
      <div 
        className="absolute left-full top-0 ml-1 w-48 bg-card border border-border rounded-lg shadow-lg z-20 py-1"
        onClick={(e) => e.stopPropagation()}
      >
        {isRenaming ? (
          <div className="px-2 py-1">
            <input
              type="text"
              value={renameValue}
              onChange={(e) => setRenameValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleRenameSubmit();
                if (e.key === 'Escape') setIsRenaming(false);
              }}
              autoFocus
              className="w-full px-2 py-1 text-xs bg-secondary border border-border rounded outline-none"
            />
            <div className="flex gap-1 mt-1">
              <button onClick={handleRenameSubmit} className="text-xs text-primary hover:underline">OK</button>
              <button onClick={() => setIsRenaming(false)} className="text-xs text-muted-foreground hover:underline">Cancel</button>
            </div>
          </div>
        ) : (
          <>
            <button
              onClick={() => { onSelectSession(session.id); onClose(); }}
              className="w-full text-left px-3 py-1.5 text-xs hover:bg-accent flex items-center gap-2"
            >
              Open
            </button>
            <button
              onClick={() => setIsRenaming(true)}
              className="w-full text-left px-3 py-1.5 text-xs hover:bg-accent flex items-center gap-2"
            >
              <Pencil size={12} /> Rename
            </button>
            <button
              onClick={() => { onDuplicate(session.id); onClose(); }}
              className="w-full text-left px-3 py-1.5 text-xs hover:bg-accent flex items-center gap-2"
            >
              <Copy size={12} /> Duplicate
            </button>
            <button
              onClick={() => { onExport(session.id); onClose(); }}
              className="w-full text-left px-3 py-1.5 text-xs hover:bg-accent flex items-center gap-2"
            >
              <Download size={12} /> Export
            </button>
            <div className="border-t border-border my-1" />
            <button
              onClick={() => { onDelete(session.id); onClose(); }}
              className="w-full text-left px-3 py-1.5 text-xs hover:bg-destructive/10 text-destructive flex items-center gap-2"
            >
              <Trash2 size={12} /> Delete
            </button>
          </>
        )}
      </div>
    </div>
  );
}

function groupByDate(sessions: Session[]) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 86400000);
  const week = new Date(today.getTime() - 7 * 86400000);

  const groups: { label: string; items: Session[] }[] = [
    { label: 'Today', items: [] },
    { label: 'Yesterday', items: [] },
    { label: 'Previous 7 Days', items: [] },
    { label: 'Older', items: [] },
  ];

  sessions.forEach(s => {
    const d = new Date(s.updated_at || s.created_at);
    if (d >= today) groups[0].items.push(s);
    else if (d >= yesterday) groups[1].items.push(s);
    else if (d >= week) groups[2].items.push(s);
    else groups[3].items.push(s);
  });

  return groups.filter(g => g.items.length > 0);
}

export default function Sidebar({ isOpen, onToggle, currentSessionId, onSelectSession, onNewChat, config, onConfigChange }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [contextMenu, setContextMenu] = useState<{ sessionId: string; x: number; y: number } | null>(null);

  // Close context menu on outside click
  useEffect(() => {
    const handleClick = () => setContextMenu(null);
    if (contextMenu) {
      window.addEventListener('click', handleClick);
      return () => window.removeEventListener('click', handleClick);
    }
  }, [contextMenu]);

  const { data: sessions = [] } = useQuery<Session[]>({
    queryKey: ['sessions'],
    queryFn: async () => {
      const res = await fetch(`${API}/sessions`);
      if (!res.ok) return [];
      return res.json();
    },
    refetchInterval: 5000,
  });

  const filtered = sessions.filter(s =>
    s.title.toLowerCase().includes(search.toLowerCase())
  );
  const groups = groupByDate(filtered);

  const deleteSession = async (id: string) => {
    await fetch(`${API}/sessions/${id}`, { method: 'DELETE' });
    queryClient.invalidateQueries({ queryKey: ['sessions'] });
    if (currentSessionId === id) onNewChat();
  };

  const renameSession = async (id: string, newTitle: string) => {
    await fetch(`${API}/sessions/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newTitle }),
    });
    queryClient.invalidateQueries({ queryKey: ['sessions'] });
  };

  const duplicateSession = async (id: string) => {
    const session = sessions.find(s => s.id === id);
    if (!session) return;
    
    // Create a new session with similar title
    const newTitle = `${session.title} (Copy)`;
    const newSession = await fetch(`${API}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        title: newTitle,
        active_provider: session.active_provider,
        active_model: session.active_model,
      }),
    });
    const created = await newSession.json();
    
    queryClient.invalidateQueries({ queryKey: ['sessions'] });
    onSelectSession(created.id);
  };

  const exportSession = async (id: string) => {
    const res = await fetch(`${API}/sessions/${id}`);
    const data = await res.json();
    
    // Create markdown content
    let content = `# ${data.session.title}\n\n`;
    content += `Created: ${new Date(data.session.created_at).toLocaleString()}\n`;
    content += `Messages: ${data.messages.length}\n\n`;
    content += `---\n\n`;
    
    for (const msg of data.messages) {
      const role = msg.role === 'user' ? 'User' : 'Assistant';
      content += `## ${role}\n\n${msg.content}\n\n`;
      if (msg.citations && msg.citations.length > 0) {
        content += `**Sources:**\n`;
        for (const cit of msg.citations) {
          content += `- ${cit.episode_title}\n`;
        }
        content += `\n`;
      }
      content += `---\n\n`;
    }
    
    // Download file
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${data.session.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleContextMenu = (e: React.MouseEvent, sessionId: string) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({ sessionId, x: e.clientX, y: e.clientY });
  };

  if (!isOpen) {
    return (
      <div className="w-12 bg-secondary flex flex-col items-center py-4 border-r border-border">
        <button onClick={onToggle} className="p-2 hover:bg-accent rounded-md transition-colors" title="Open sidebar">
          <ChevronRight size={18} />
        </button>
      </div>
    );
  }

  return (
    <div className="w-64 bg-secondary flex flex-col h-full border-r border-border shrink-0">
      {/* Top actions */}
      <div className="p-3 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-bold tracking-wide text-foreground">Lenny</span>
          <button onClick={onToggle} className="p-1 hover:bg-accent rounded-md transition-colors" title="Collapse sidebar">
            <ChevronLeft size={16} />
          </button>
        </div>
        <button onClick={onNewChat}
          className="flex items-center gap-2 w-full px-3 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
          <MessageSquarePlus size={16} />
          New Chat
        </button>
      </div>

      {/* Navigation */}
      <nav className="px-3 space-y-1">
        <button onClick={() => navigate('/knowledge')}
          className={`flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm transition-colors ${location.pathname === '/knowledge' ? 'bg-accent font-medium' : 'hover:bg-accent/50'}`}>
          <Database size={16} />
          Knowledge Base
        </button>
        <button onClick={() => navigate('/artifacts')}
          className={`flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm transition-colors ${location.pathname === '/artifacts' ? 'bg-accent font-medium' : 'hover:bg-accent/50'}`}>
          <Box size={16} />
          Artifacts
        </button>
      </nav>

      {/* Search */}
      <div className="px-3 mt-3">
        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-2.5 text-muted-foreground" />
          <input type="text" placeholder="Search chats..."
            value={search} onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-background text-foreground pl-8 pr-3 py-2 rounded-lg text-xs outline-none border border-border focus:ring-1 focus:ring-primary/30" />
        </div>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto px-3 mt-2">
        {groups.map(group => (
          <div key={group.label} className="mb-3">
            <div className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider px-1 mb-1">
              {group.label}
            </div>
            {group.items.map(s => (
              <div 
                key={s.id} 
                className="group flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-sm transition-colors mb-0.5 hover:bg-accent/50"
                style={{ 
                  backgroundColor: currentSessionId === s.id ? 'var(--accent)' : undefined,
                  fontWeight: currentSessionId === s.id ? 500 : undefined
                }}
              >
                <button 
                  onClick={() => onSelectSession(s.id)}
                  className="flex-1 text-left truncate"
                >
                  {s.title || 'New Chat'}
                </button>
                <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleContextMenu(e, s.id); }}
                    className="p-0.5 hover:bg-accent rounded transition-colors"
                    title="More options"
                  >
                    <MoreVertical size={12} />
                  </button>
                  <button 
                    onClick={(e) => { e.stopPropagation(); deleteSession(s.id); }}
                    className="p-0.5 hover:text-destructive transition-colors"
                    title="Delete"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* User Profile / Settings Toggle */}
      <div className="p-3 border-t border-border">
        <button 
          onClick={() => setIsSettingsOpen(true)}
          className="flex items-center gap-3 w-full p-2 hover:bg-accent/50 rounded-lg transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
            <User size={16} className="text-primary" />
          </div>
          <div className="flex-1 text-left">
            <div className="text-sm font-medium text-foreground">My Profile</div>
            <div className="text-[10px] text-muted-foreground uppercase">{config.provider}</div>
          </div>
          <Settings size={16} className="text-muted-foreground" />
        </button>
      </div>

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
        config={config} 
        onConfigChange={onConfigChange} 
      />

      {/* Context Menu */}
      {contextMenu && (
        <div
          className="fixed z-50"
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          <SessionContextMenu
            session={sessions.find(s => s.id === contextMenu.sessionId)!}
            currentSessionId={currentSessionId}
            onSelectSession={(id) => { onSelectSession(id); setContextMenu(null); }}
            onDelete={async (id) => { await deleteSession(id); setContextMenu(null); }}
            onRename={async (id, title) => { await renameSession(id, title); setContextMenu(null); }}
            onDuplicate={async (id) => { await duplicateSession(id); setContextMenu(null); }}
            onExport={async (id) => { await exportSession(id); setContextMenu(null); }}
            onClose={() => setContextMenu(null)}
          />
        </div>
      )}
    </div>
  );
}
