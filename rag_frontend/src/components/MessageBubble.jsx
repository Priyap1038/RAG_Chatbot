// src/components/MessageBubble.jsx
// ─────────────────────────────────────────────────────
// Renders a single chat message — user OR assistant.
// Shows source document badges on bot messages.
// Supports a "typing" state while streaming.
// ─────────────────────────────────────────────────────

export default function MessageBubble({ role, content, sources, isTyping }) {
    const isUser = role === 'user';

    return (
        <div className={`flex gap-3 msg-enter ${isUser ? 'justify-end' : 'justify-start'}`}>

            {/* Avatar — only for bot */}
            {!isUser && (
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 mt-1">
                    AI
                </div>
            )}

            <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1.5`}>

                {/* Bubble */}
                <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
          ${isUser
                        ? 'bg-indigo-600 text-white rounded-tr-sm'
                        : 'bg-[#1e1e2e] text-white/90 border border-white/10 rounded-tl-sm'}`}
                >
                    {content}
                    {isTyping && <span className="typing-cursor" />}
                </div>
            </div>

            {/* Avatar — only for user */}
            {isUser && (
                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 mt-1">
                    U
                </div>
            )}
        </div>
    );
}
