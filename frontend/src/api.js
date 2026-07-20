const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// POST the chat history, parse the SSE stream, invoke onEvent per event.
export async function streamChat(messages, onEvent) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split("\n\n");   // SSE events are separated by blank lines
    buffer = parts.pop();                  // keep incomplete chunk for next read
    for (const part of parts) {
      if (part.startsWith("data: ")) {
        onEvent(JSON.parse(part.slice(6)));
      }
    }
  }
}

export const mediaUrl = (path) => (path ? `${BASE}${path}` : null);