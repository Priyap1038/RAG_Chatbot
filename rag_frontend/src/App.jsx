// src/App.jsx
// ─────────────────────────────────────────────────────
// Root component — wires sidebar + chat window together.
// Session ID and messages are persisted in localStorage
// so a page refresh restores exactly where the user was.
// ─────────────────────────────────────────────────────

import { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { fetchSessions, fetchHistory, deleteSession, createSession } from './api';

// Generate a short random session ID
function newSessionId() {
  return 'sess_' + Math.random().toString(36).slice(2, 10);
}

export default function App() {

  // ── Restore activeId from localStorage on first render ──
  const [sessions, setSessions] = useState([]);
  const [activeId, setActiveId] = useState(
    () => localStorage.getItem('activeSessionId') || null
  );
  const [activeMessages, setActiveMessages] = useState(
    () => {
      try { return JSON.parse(localStorage.getItem('activeMessages') || '[]'); }
      catch { return []; }
    }
  );

  // ── Persist activeId to localStorage whenever it changes ──
  useEffect(() => {
    if (activeId) localStorage.setItem('activeSessionId', activeId);
    else localStorage.removeItem('activeSessionId');
  }, [activeId]);

  // ── Persist messages to localStorage whenever they change ──
  useEffect(() => {
    localStorage.setItem('activeMessages', JSON.stringify(activeMessages));
  }, [activeMessages]);

  // ── On mount: re-fetch history from backend to stay in sync ──
  // (covers the case where backend restarted and memory was wiped)
  useEffect(() => {
    const savedId = localStorage.getItem('activeSessionId');
    if (!savedId) return;
    fetchHistory(savedId)
      .then(data => {
        if (data.messages.length > 0) {
          setActiveMessages(data.messages.map(m => ({
            role: m.role,
            content: m.content,
            sources: null,
            isTyping: false,
          })));
        }
      })
      .catch(() => { }); // session might not exist in backend yet — that's OK
  }, []); // run once on mount only

  // ── Load sidebar sessions from backend ──────────────
  const refreshSessions = useCallback(async () => {
    try {
      const data = await fetchSessions();
      setSessions(data);
    } catch {
      // backend not reachable yet — silent fail
    }
  }, []);

  // Poll every 5 seconds so sidebar stays fresh
  useEffect(() => {
    refreshSessions();
    const id = setInterval(refreshSessions, 5000);
    return () => clearInterval(id);
  }, [refreshSessions]);

  // ── Session actions ──────────────────────────────────
  async function handleSelectSession(sid) {
    // Clear FIRST so ChatWindow remounts with [] — not the previous session's messages.
    setActiveMessages([]);
    setActiveId(sid);
    try {
      const data = await fetchHistory(sid);
      setActiveMessages(data.messages.map(m => ({
        role: m.role,
        content: m.content,
        sources: null,
        isTyping: false,
      })));
    } catch {
      setActiveMessages([]);
    }
  }

  async function handleNewSession() {
    const id = newSessionId();
    setActiveId(id);
    setActiveMessages([]);
    localStorage.setItem('activeSessionId', id);
    localStorage.setItem('activeMessages', '[]');
    // 1. Register session on BACKEND immediately
    try { await createSession(id); } catch { /* silent — backend may not be ready */ }
    // 2. Refresh sidebar from backend so it shows the real session
    await refreshSessions();
  }

  async function handleDeleteSession(sid) {
    await deleteSession(sid);
    if (activeId === sid) {
      setActiveId(null);
      setActiveMessages([]);
      localStorage.removeItem('activeSessionId');
      localStorage.setItem('activeMessages', '[]');
    }
    await refreshSessions();
  }

  return (
    <div className="flex h-screen bg-[#0d0d1a] overflow-hidden">
      <Sidebar
        sessions={sessions}
        activeSession={activeId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
      />

      {activeId ? (
        <ChatWindow
          key={activeId}              /* remount on session switch */
          sessionId={activeId}
          initialMessages={activeMessages}
          onSessionUpdated={refreshSessions}
          onMessagesChange={setActiveMessages}   /* keep localStorage in sync during chat */
        />
      ) : (
        /* ── Landing / no session selected ── */
        <div className="flex-1 flex flex-col items-center justify-center gap-6 bg-[#0d0d1a]">
          <div className="w-20 h-20 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
            <svg className="w-10 h-10 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div className="text-center">
            <h1 className="text-white text-2xl font-bold">Acme Tech RAG Assistant</h1>
            <p className="text-white/40 text-sm mt-2 max-w-sm">
              Click <span className="text-indigo-400 font-medium">New Chat</span> in the sidebar to start asking questions about Acme&apos;s history, products, and HR policies.
            </p>
          </div>
          <button
            onClick={handleNewSession}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-colors"
          >
            Start New Chat
          </button>
        </div>
      )}
    </div>
  );
}
