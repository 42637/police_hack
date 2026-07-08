import React, { useState, useEffect, useRef } from 'react';
import { apiClient } from '../api/client';
import { 
  Bot, Send, Database, BarChart3, ListCollapse, 
  Table, ChevronRight, HelpCircle, History
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import toast from 'react-hot-toast';

export const Section3: React.FC = () => {
  const [sessions, setSessions] = useState<any[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('');
  const [messages, setMessages] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [sending, setSending] = useState(false);
  const [dbStats, setDbStats] = useState<any>(null);
  
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Load chat sessions and stats on boot
  useEffect(() => {
    const initChat = async () => {
      try {
        const [sessionRes, statsRes] = await Promise.all([
          apiClient.get('/chat/sessions'),
          apiClient.get('/dashboard/stats')
        ]);
        
        setSessions(sessionRes.data);
        setDbStats(statsRes.data.stats);
        
        // If sessions exist, auto-select first one, otherwise create a new one
        if (sessionRes.data.length > 0) {
          selectSession(sessionRes.data[0].session_id);
        } else {
          createNewSession();
        }
      } catch (err) {
        console.error(err);
      }
    };
    initChat();
  }, []);

  // Scroll to bottom on message updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const createNewSession = () => {
    const newId = `session_${Date.now()}`;
    setActiveSessionId(newId);
    setMessages([]);
    // Prepend to sessions list locally
    setSessions(prev => [{ session_id: newId, title: 'New Operations Query', updated_at: new Date().toISOString() }, ...prev]);
  };

  const selectSession = async (sessionId: string) => {
    setActiveSessionId(sessionId);
    try {
      const response = await apiClient.get(`/chat/sessions/${sessionId}`);
      setMessages(response.data.messages || []);
    } catch (err) {
      toast.error('Failed to load session message history.');
      console.error(err);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || query;
    if (!text.trim()) return;

    setQuery('');
    setSending(true);

    // Optimistically append user message locally
    const userMsg = { role: 'user', content: text, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);

    try {
      const response = await apiClient.post('/chat', {
        query: text,
        session_id: activeSessionId
      });
      
      const assistantMsg = {
        role: 'assistant',
        content: response.data.response,
        metadata: response.data.metadata,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMsg]);
      
      // Update session title locally based on user first query
      setSessions(prev => 
        prev.map(s => s.session_id === activeSessionId ? { ...s, title: text.substring(0, 30) } : s)
      );
    } catch (err: any) {
      toast.error('AI assistant processing error.');
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const suggestions = [
    "List all cloned vehicles detected",
    "Show vehicle statistics summary chart",
    "Vehicles detected in Hyderabad outer ring road",
    "List high risk plates flagged today"
  ];

  return (
    <div className="h-[80vh] flex border border-gray-800 rounded-lg overflow-hidden glass-panel">
      
      {/* 1. Left Conversation History Sidebar */}
      <aside className="w-64 border-r border-gray-800 bg-gray-950/40 flex flex-col shrink-0 hidden md:flex font-mono text-xs">
        <div className="p-4 border-b border-gray-900 flex justify-between items-center">
          <span className="font-bold text-cyan-400 tracking-wider">HISTORY SEGMENTS</span>
          <button 
            onClick={createNewSession}
            className="border border-cyan-500/30 hover:border-cyan-400 px-2 py-1 rounded text-[10px] text-cyan-400 transition-all duration-300"
          >
            + NEW TERM
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {sessions.map(s => (
            <button
              key={s.session_id}
              onClick={() => selectSession(s.session_id)}
              className={`w-full text-left p-3 rounded transition-all duration-200 border flex items-start space-x-2.5 ${
                s.session_id === activeSessionId 
                  ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300 font-bold' 
                  : 'border-transparent text-gray-500 hover:text-gray-300 hover:bg-gray-900/30'
              }`}
            >
              <History className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              <span className="truncate">{s.title || 'Operational Log'}</span>
            </button>
          ))}
        </div>
      </aside>

      {/* 2. Center Chat Terminal Panel */}
      <div className="flex-1 flex flex-col bg-gray-950/20">
        
        {/* Header bar */}
        <div className="h-14 border-b border-gray-800 px-5 flex items-center justify-between bg-gray-950/40 shrink-0">
          <div className="flex items-center space-x-2 font-mono text-xs">
            <Bot className="w-4 h-4 text-purple-400" />
            <span className="font-bold text-white uppercase">SENTINEL SECURE AI ASSISTANT</span>
          </div>
          <div className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-950">
            SECURE QUERY MODE // RAG ON-PREM
          </div>
        </div>

        {/* Messages list */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-6">
              <Bot className="w-12 h-12 text-gray-700 animate-pulse" />
              <div className="space-y-1 max-w-md">
                <h4 className="text-sm font-bold text-gray-300 uppercase font-mono">INTELLIGENCE AGENT DORMANT</h4>
                <p className="text-xs text-gray-500 font-mono uppercase">
                  Secure RAG chatbot. Answers are generated strictly from on-prem MongoDB vehicle registries and detections.
                </p>
              </div>

              {/* Suggestions Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full font-mono text-[10px] text-left">
                {suggestions.map(s => (
                  <button
                    key={s}
                    onClick={() => handleSend(s)}
                    className="p-3 border border-gray-900 bg-gray-950/60 rounded-lg hover:border-cyan-500/30 hover:bg-cyan-500/5 text-gray-400 hover:text-cyan-300 transition-all duration-300 flex items-center justify-between"
                  >
                    <span>{s}</span>
                    <ChevronRight className="w-3 h-3" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, idx) => (
            <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-xl p-4 font-mono text-xs space-y-3 ${
                m.role === 'user' 
                  ? 'bg-purple-950/20 border border-purple-500/20 text-purple-200' 
                  : 'bg-cyan-950/20 border border-cyan-500/20 text-cyan-200 shadow-[0_0_15px_rgba(6,182,212,0.02)]'
              }`}>
                {/* Header label */}
                <div className="flex items-center justify-between border-b border-gray-900 pb-1.5 text-[9px] text-gray-500">
                  <span className="uppercase font-bold tracking-wider">
                    {m.role === 'user' ? 'OPERATOR CLEARANCE' : 'SENTINEL COGNITION'}
                  </span>
                  <span>{new Date(m.timestamp).toLocaleTimeString()}</span>
                </div>
                
                {/* Content formatted */}
                <div className="whitespace-pre-wrap leading-relaxed">
                  {m.content}
                </div>

                {/* Render Attachments from Metadata (Tables, Charts) */}
                {m.metadata && (
                  <div className="pt-3 border-t border-gray-900 space-y-3">
                    
                    {/* Render attachment table */}
                    {m.metadata.type === 'table' && (
                      <div className="overflow-x-auto border border-gray-900 rounded bg-gray-950/60 max-w-full">
                        <table className="w-full text-left text-[10px] leading-normal font-mono">
                          <thead>
                            <tr className="bg-gray-950 border-b border-gray-900 text-gray-500">
                              {m.metadata.columns.map((col: string) => (
                                <th key={col} className="p-2 uppercase tracking-wider">{col.replace('_', ' ')}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-900/50">
                            {m.metadata.data?.map((row: any, rIdx: number) => (
                              <tr key={row.id || rIdx} className="hover:bg-cyan-500/5">
                                {m.metadata.columns.map((col: string) => (
                                  <td key={col} className="p-2 text-gray-300">
                                    {col === 'risk_level' ? (
                                      <span className={`px-1.5 py-0.5 rounded font-bold ${
                                        row[col] === 'Critical' ? 'bg-red-500/10 text-red-500' :
                                        row[col] === 'High' ? 'bg-orange-500/10 text-orange-400' :
                                        'bg-emerald-500/10 text-emerald-400'
                                      }`}>
                                        {row[col]}
                                      </span>
                                    ) : row[col]}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}

                    {/* Render attachment chart */}
                    {m.metadata.type === 'chart' && (
                      <div className="p-3 bg-gray-950/60 border border-gray-900 rounded h-40">
                        <span className="text-[9px] text-gray-500 uppercase font-bold block mb-2">INTELLIGENCE PLOT</span>
                        <ResponsiveContainer width="100%" height="80%">
                          <BarChart data={m.metadata.data}>
                            <XAxis dataKey="name" stroke="#6b7280" fontSize={8} fontFamily="monospace" />
                            <YAxis stroke="#6b7280" fontSize={8} fontFamily="monospace" />
                            <Bar dataKey="value" fill="#06b6d4" radius={[2, 2, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                  </div>
                )}

              </div>
            </div>
          ))}

          {/* Typing Loading Indicator */}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-cyan-950/20 border border-cyan-500/20 rounded-xl p-4 font-mono text-xs space-y-2 text-cyan-400">
                <span className="text-[9px] text-gray-500 uppercase block font-bold">COGNITION SCANNING DB...</span>
                <div className="flex space-x-1.5 py-1">
                  <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Form Message input */}
        <div className="p-4 border-t border-gray-800 bg-gray-950/40 shrink-0">
          <div className="flex items-center space-x-3 bg-gray-950 border border-gray-800 rounded-lg p-1">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask Sentinel database (e.g. 'Show statistics summary count chart', 'List clones')"
              className="flex-1 bg-transparent px-3 py-2 text-xs font-mono text-cyan-400 placeholder-gray-600 focus:outline-none"
            />
            <button
              onClick={() => handleSend()}
              disabled={sending || !query.trim()}
              className="bg-cyan-500 hover:bg-cyan-400 disabled:bg-cyan-950 p-2 rounded text-gray-950 transition-all duration-300"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

      </div>

      {/* 3. Right Database Statistics Panel */}
      <aside className="w-60 border-l border-gray-800 bg-gray-950/40 p-4 shrink-0 hidden lg:block font-mono text-xs space-y-6">
        <div>
          <h3 className="font-bold text-cyan-400 tracking-wider border-b border-gray-900 pb-2 uppercase">RADAR DATABASES ACTIVE</h3>
        </div>
        
        {dbStats ? (
          <div className="space-y-4">
            <div className="p-3 border border-gray-900 bg-gray-950/60 rounded">
              <span className="text-gray-500 uppercase text-[9px] block">REGISTRY RECORDS</span>
              <span className="text-md font-bold text-white">{dbStats.vehicles_detected + 5} PLATES</span>
            </div>
            <div className="p-3 border border-gray-900 bg-gray-950/60 rounded">
              <span className="text-gray-500 uppercase text-[9px] block">SYSTEM LOG DETECTIONS</span>
              <span className="text-md font-bold text-cyan-400">{dbStats.today_uploads} TODAY</span>
            </div>
            <div className="p-3 border border-gray-900 bg-rose-950/15 rounded border-rose-950/30">
              <span className="text-rose-500 uppercase text-[9px] block">FLAG_CLONE ENTRIES</span>
              <span className="text-md font-bold text-rose-500">{dbStats.cloned_vehicles} TICKETS</span>
            </div>
          </div>
        ) : (
          <div className="animate-pulse space-y-3">
            <div className="h-10 bg-gray-900 rounded"></div>
            <div className="h-10 bg-gray-900 rounded"></div>
            <div className="h-10 bg-gray-900 rounded"></div>
          </div>
        )}

        <div className="p-3 bg-gray-900/60 rounded text-[9px] text-gray-500 leading-normal leading-relaxed">
          The securing assistant utilizes pre-defined parsing pipelines. It checks spatial and visual indices on-premise. Hallucinatory summaries are filtered.
        </div>
      </aside>

    </div>
  );
};
