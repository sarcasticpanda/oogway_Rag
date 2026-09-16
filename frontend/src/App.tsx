import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import ChatArea from './components/chat/ChatArea';
import ArtifactsPage from './components/artifacts/ArtifactsPage';
import SettingsModal from './components/settings/SettingsModal';
import KnowledgeBasePage from './components/knowledge/KnowledgeBasePage';

export interface AppConfig {
  provider: string;
  model: string;
  apiKey?: string;
  customProviderUrl?: string;
  responseStyle?: string;
  responseInstructions?: string;
}

export default function App() {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [config, setConfig] = useState<AppConfig>({ provider: 'groq', model: '' });
  const navigate = useNavigate();

  // Fetch backend model configuration on mount
  useEffect(() => {
    const fetchModelConfig = async () => {
      try {
        const response = await fetch('/api/v1/models');
        const data = await response.json();
        setConfig({
          provider: data.active_provider || 'groq',
          model: data.active_model || ''
        });
      } catch (error) {
        console.error('Failed to fetch model configuration:', error);
      }
    };
    fetchModelConfig();
  }, []);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background text-foreground">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        currentSessionId={currentSessionId}
        onSelectSession={(id) => { setCurrentSessionId(id); navigate('/'); }}
        onNewChat={() => { setCurrentSessionId(null); navigate('/'); }}
        config={config}
        onConfigChange={setConfig}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        <Routes>
          <Route path="/" element={
            <ChatArea
              sessionId={currentSessionId}
              onSessionCreated={setCurrentSessionId}
              config={config}
              onConfigChange={setConfig}
            />
          } />
          <Route path="/artifacts" element={<ArtifactsPage />} />
          <Route path="/knowledge" element={<KnowledgeBasePage />} />
        </Routes>
      </main>
    </div>
  );
}
