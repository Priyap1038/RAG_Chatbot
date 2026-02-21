// src/components/ChatWindow.jsx
// ─────────────────────────────────────────────────────
// The main chat area:
//   • Scrollable conversation history
//   • Input box at the bottom
//   • Send button (also triggered by Enter key)
//   • Streams SSE tokens from POST /api/chat
// ─────────────────────────────────────────────────────

import { useState, useRef, useEffect, useCallback } from 'react';
import MessageBubble from './MessageBubble';
import { sendChat } from '../api';

export default function ChatWindow({ sessionId, initialMessages, onSessionUpdated, onMessagesChange }) {
    const [messages, setMessages] = useState(initialMessages || []);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef(null);
    const inputRef = useRef(null);

    // Wrapper: update state AND notify parent (keeps localStorage in sync)
    const updateMessages = useCallback((updater) => {
        setMessages(prev => {
            const next = typeof updater === 'function' ? updater(prev) : updater;
            onMessagesChange?.(next);
            return next;
        });
    }, [onMessagesChange]);

    // Sync messages whenever the session changes OR when the parent delivers
    // fetched history after an async load. Use setMessages directly (NOT
    // updateMessages) so this restore path never writes back to localStorage —
    // that avoids the bug where stale previous-session messages overwrite a
    // different session's localStorage slot.
    useEffect(() => {
        setMessages(initialMessages || []);
    }, [sessionId, initialMessages]); // eslint-disable-line react-hooks/exhaustive-deps

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Focus input on load
    useEffect(() => { inputRef.current?.focus(); }, [sessionId]);

    async function handleSend() {
        const text = input.trim();
        if (!text || loading) return;

        const userMsg = { role: 'user', content: text };
        updateMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        // Add a placeholder bot message that we'll stream into
        const botPlaceholder = { role: 'assistant', content: '', sources: null, isTyping: true };
        updateMessages(prev => [...prev, botPlaceholder]);

        try {
            const response = await sendChat(text, sessionId);
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let botText = '';
            let sources = null;

            // Read the SSE stream token by token
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });

                // Each SSE event looks like:  data: {"token":"hello"}\n\n
                for (const line of chunk.split('\n')) {
                    if (!line.startsWith('data: ')) continue;
                    try {
                        const payload = JSON.parse(line.slice(6));

                        if (payload.done) {
                            // Final event contains source list
                            sources = payload.sources || [];
                        } else if (payload.token !== undefined) {
                            botText += payload.token;
                        }

                        // Update the last (bot) message in state
                        updateMessages(prev => {
                            const updated = [...prev];
                            updated[updated.length - 1] = {
                                role: 'assistant',
                                content: botText,
                                sources: payload.done ? sources : null,
                                isTyping: !payload.done,
                            };
                            return updated;
                        });
                    } catch {
                        // skip malformed lines
                    }
                }
            }

            // Notify parent so sidebar session list refreshes
            onSessionUpdated?.();

        } catch (err) {
            updateMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                    role: 'assistant',
                    content: '⚠️ Error: Could not reach the backend. Make sure the server is running on port 8000.',
                    sources: [],
                    isTyping: false,
                };
                return updated;
            });
        } finally {
            setLoading(false);
        }
    }

    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }

    return (
        <div className="flex flex-col flex-1 h-screen bg-[#0d0d1a]">

            {/* ── Header ── */}
            <div className="px-6 py-4 border-b border-white/10 flex items-center gap-3 bg-[#12121f]">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-white/70 text-sm font-medium">
                    {sessionId ? `Session: ${sessionId.slice(0, 8)}…` : 'No session selected'}
                </span>
                <span className="ml-auto text-white/25 text-xs">Backend: localhost:8000</span>
            </div>

            {/* ── Conversation History (scroll area) ── */}
            <div className="flex-1 overflow-y-auto px-4 py-6 space-y-5">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
                        <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
                            <svg className="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                            </svg>
                        </div>
                        <div>
                            <p className="text-white/70 font-semibold text-lg">Ask Acme's AI Assistant</p>
                            <p className="text-white/30 text-sm mt-1 max-w-xs">
                                Ask anything about company history, products, or HR policies.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-2 justify-center mt-2">
                            {['What products does Acme offer?', 'What is the leave policy?', 'When was Acme founded?'].map(q => (
                                <button
                                    key={q}
                                    onClick={() => { setInput(q); inputRef.current?.focus(); }}
                                    className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-white/50 text-xs hover:bg-white/10 hover:text-white/80 transition-colors"
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <MessageBubble
                        key={i}
                        role={msg.role}
                        content={msg.content}
                        sources={msg.sources}
                        isTyping={msg.isTyping}
                    />
                ))}
                <div ref={bottomRef} />
            </div>

            {/* ── Input Box + Send Button ── */}
            <div className="px-4 pb-5 pt-3 bg-[#12121f] border-t border-white/10">
                <div className="flex items-end gap-3 bg-[#1e1e2e] border border-white/10 rounded-2xl px-4 py-3 focus-within:border-indigo-500/60 transition-colors">
                    <textarea
                        ref={inputRef}
                        rows={1}
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about Acme Tech Solutions… (Enter to send)"
                        disabled={loading}
                        className="flex-1 bg-transparent text-white text-sm placeholder-white/25 resize-none outline-none leading-relaxed max-h-36 overflow-y-auto disabled:opacity-50"
                        style={{ fieldSizing: 'content' }}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                        className="flex-shrink-0 w-9 h-9 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center transition-all"
                        title="Send (Enter)"
                    >
                        {loading ? (
                            <svg className="w-4 h-4 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                            </svg>
                        ) : (
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        )}
                    </button>
                </div>
                <p className="text-center text-white/15 text-xs mt-2">
                    Shift+Enter for new line
                </p>
            </div>
        </div>
    );
}
