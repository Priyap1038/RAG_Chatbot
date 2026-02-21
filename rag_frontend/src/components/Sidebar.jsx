// src/components/Sidebar.jsx
// ─────────────────────────────────────────────────────
// Left sidebar: list of past sessions + new chat button
// + document upload section
// ─────────────────────────────────────────────────────

import { useState, useRef } from 'react';
import { ingestFile } from '../api';

export default function Sidebar({ sessions, activeSession, onSelectSession, onNewSession, onDeleteSession }) {
    const [uploading, setUploading] = useState(false);
    const [uploadMsg, setUploadMsg] = useState('');
    const fileRef = useRef();

    async function handleFileUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        setUploading(true);
        setUploadMsg('');
        try {
            const res = await ingestFile(file);
            setUploadMsg(`✅ ${res.message}`);
        } catch {
            setUploadMsg('❌ Upload failed. Check file type (.txt / .md).');
        } finally {
            setUploading(false);
            fileRef.current.value = '';
        }
    }

    return (
        <aside className="w-64 min-h-screen bg-[#12121f] border-r border-white/10 flex flex-col">

            {/* ── Logo ── */}
            <div className="px-5 py-5 border-b border-white/10">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white text-sm font-bold">A</div>
                    <div>
                        <p className="text-white font-semibold text-sm leading-tight">Acme Tech</p>
                        <p className="text-white/40 text-xs">RAG Chatbot</p>
                    </div>
                </div>
            </div>

            {/* ── New Chat ── */}
            <div className="px-4 py-3">
                <button
                    onClick={onNewSession}
                    className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Chat
                </button>
            </div>

            {/* ── Session List ── */}
            <div className="flex-1 overflow-y-auto px-2 space-y-0.5 pb-2">
                <p className="text-white/30 text-xs font-semibold uppercase tracking-widest px-2 mb-2 mt-1">Recent Chats</p>
                {sessions.length === 0 && (
                    <p className="text-white/25 text-xs px-2 py-2">No chats yet. Start one!</p>
                )}
                {sessions.map((s) => (
                    <div
                        key={s.session_id}
                        onClick={() => onSelectSession(s.session_id)}
                        className={`group flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-colors
              ${activeSession === s.session_id
                                ? 'bg-indigo-600/20 text-white border border-indigo-500/40'
                                : 'text-white/60 hover:bg-white/5 hover:text-white border border-transparent'}`}
                    >
                        <div className="min-w-0 flex-1">
                            <p className="text-sm truncate font-medium">{s.title || 'New Chat'}</p>
                            <p className="text-xs text-white/30 mt-0.5">{s.message_count} msgs</p>
                        </div>
                        <button
                            onClick={(e) => { e.stopPropagation(); onDeleteSession(s.session_id); }}
                            className="opacity-0 group-hover:opacity-100 ml-2 p-1 rounded hover:bg-white/10 text-white/40 hover:text-red-400 transition-all"
                            title="Delete session"
                        >
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                ))}
            </div>

            {/* ── Document Upload ── */}
            <div className="px-4 py-4 border-t border-white/10">
                <p className="text-white/40 text-xs font-semibold uppercase tracking-widest mb-2">Upload Document</p>
                <label className={`flex items-center gap-2 w-full px-3 py-2 rounded-lg border border-dashed 
          ${uploading ? 'border-indigo-400/40 cursor-not-allowed' : 'border-white/20 hover:border-indigo-400/60 cursor-pointer'} 
          transition-colors`}>
                    <svg className="w-4 h-4 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    <span className="text-white/40 text-xs">{uploading ? 'Uploading…' : '.txt or .md file'}</span>
                    <input ref={fileRef} type="file" accept=".txt,.md" className="hidden" onChange={handleFileUpload} disabled={uploading} />
                </label>
                {uploadMsg && <p className="mt-1.5 text-xs text-white/50 leading-tight">{uploadMsg}</p>}
            </div>
        </aside>
    );
}
