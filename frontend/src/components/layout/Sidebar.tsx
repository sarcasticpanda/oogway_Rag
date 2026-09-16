import { MessageSquarePlus, FileText, Box, Settings, ChevronLeft, ChevronRight, Trash2, Search, Database, User } from 'lucide-react';
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

  // Keyboard shortcut: Ctrl+N / Cmd+N creates a new chat
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'n') {
        e.preventDefault();
        onNewChat();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onNewChat]);

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

  const deleteSession = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await fetch(`${API}/sessions/${id}`, { method: 'DELETE' });
    queryClient.invalidateQueries({ queryKey: ['sessions'] });
    if (currentSessionId === id) onNewChat();
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
              <button key={s.id} onClick={() => onSelectSession(s.id)}
                className={`group flex items-center justify-between w-full px-2.5 py-1.5 rounded-lg text-sm transition-colors mb-0.5 ${
                  currentSessionId === s.id ? 'bg-accent font-medium' : 'hover:bg-accent/50'
                }`}>
                <span className="truncate text-left flex-1">{s.title || 'New Chat'}</span>
                <button onClick={(e) => deleteSession(s.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive transition-all"
                  title="Delete">
                  <Trash2 size={12} />
                </button>
              </button>
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
    </div>
  );
}
