// src/api.js
// ─────────────────────────────────────────────────────
// All backend API calls in one file.
//
// PRODUCTION: BASE URL is read from VITE_API_URL env var.
//   Development:  leave empty → Vite proxy forwards /api/* → localhost:8000
//   Production:   set VITE_API_URL=https://api.yourapp.com in .env.production
//
// PRODUCTION: API key is read from VITE_API_KEY env var.
//   Add to .env.production if API_KEY is set on the backend.
// ─────────────────────────────────────────────────────

const BASE = import.meta.env.VITE_API_URL || '';
const API_KEY = import.meta.env.VITE_API_KEY || '';

/** Return common headers including optional Authorization */
function headers(extra = {}) {
    const h = { 'Content-Type': 'application/json', ...extra };
    if (API_KEY) h['Authorization'] = `Bearer ${API_KEY}`;
    return h;
}

/** Fetch all sessions for the sidebar */
export async function fetchSessions() {
    const res = await fetch(`${BASE}/api/sessions`, { headers: headers({ 'Content-Type': undefined }) });
    if (!res.ok) throw new Error('Failed to fetch sessions');
    const data = await res.json();
    return data.sessions;
}

/** Register a brand-new empty session on the backend immediately */
export async function createSession(sessionId) {
    const res = await fetch(`${BASE}/api/session`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ session_id: sessionId }),
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
}

/** Get full history for one session */
export async function fetchHistory(sessionId) {
    const res = await fetch(`${BASE}/api/history/${sessionId}`,
        { headers: headers({ 'Content-Type': undefined }) });
    if (!res.ok) throw new Error('Failed to fetch history');
    return res.json();
}

/** Delete a session */
export async function deleteSession(sessionId) {
    const res = await fetch(`${BASE}/api/session/${sessionId}`,
        { method: 'DELETE', headers: headers({ 'Content-Type': undefined }) });
    if (!res.ok) throw new Error('Failed to delete session');
    return res.json();
}

/** Send a chat message — returns a raw Response for SSE streaming */
export async function sendChat(message, sessionId) {
    const res = await fetch(`${BASE}/api/chat`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ message, session_id: sessionId }),
    });
    if (!res.ok) throw new Error('Chat request failed');
    return res;
}

/** Ingest a document via JSON body */
export async function ingestText(text, filename) {
    const res = await fetch(`${BASE}/api/ingest`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ text, filename }),
    });
    if (!res.ok) throw new Error('Ingest failed');
    return res.json();
}

/** Ingest a file via multipart form */
export async function ingestFile(file) {
    const form = new FormData();
    form.append('file', file);
    const h = API_KEY ? { 'Authorization': `Bearer ${API_KEY}` } : {};
    const res = await fetch(`${BASE}/api/ingest/file`, { method: 'POST', headers: h, body: form });
    if (!res.ok) throw new Error('File ingest failed');
    return res.json();
}
