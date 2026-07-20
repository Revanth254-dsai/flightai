import { useState, useRef, useEffect } from "react";
import { streamChat } from "../api.js";

const styles = {
  box: { flex: 2, display: "flex", flexDirection: "column", background: "#181c2e",
         borderRadius: 12, padding: 16, height: "75vh" },
  log: { flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 8 },
  msg: (role) => ({
    alignSelf: role === "user" ? "flex-end" : "flex-start",
    background: role === "user" ? "#3b5bfd" : "#262b40",
    padding: "8px 12px", borderRadius: 10, maxWidth: "80%", whiteSpace: "pre-wrap",
  }),
  tool: { alignSelf: "center", fontSize: 12, color: "#9aa0b5", fontStyle: "italic" },
  row: { display: "flex", gap: 8, marginTop: 12 },
  input: { flex: 1, padding: 10, borderRadius: 8, border: "1px solid #333",
           background: "#0f1220", color: "#e8e8f0" },
  btn: { padding: "10px 18px", borderRadius: 8, border: "none",
         background: "#3b5bfd", color: "white", cursor: "pointer" },
};

export default function Chat({ onMedia }) {
  const [messages, setMessages] = useState([]);   // {role, content}
  const [toolNote, setToolNote] = useState(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const logRef = useRef(null);

  useEffect(() => {
    logRef.current?.scrollTo(0, logRef.current.scrollHeight);
  }, [messages, toolNote]);

  async function send() {
    if (!input.trim() || busy) return;
    const history = [...messages, { role: "user", content: input.trim() }];
    setMessages([...history, { role: "assistant", content: "" }]);
    setInput("");
    setBusy(true);

    try {
      await streamChat(history, (e) => {
        if (e.type === "token") {
          setMessages((m) => {
            const copy = [...m];
            copy[copy.length - 1] = {
              role: "assistant",
              content: copy[copy.length - 1].content + e.content,
            };
            return copy;
          });
        } else if (e.type === "tool") {
          setToolNote(`🔧 ${e.name}(${e.arguments})`);
        } else if (e.type === "media") {
          onMedia(e);
          setToolNote(null);
        } else if (e.type === "error") {
          setToolNote(`⚠️ ${e.detail}`);
        }
      });
    } catch (err) {
      setToolNote(`⚠️ ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={styles.box}>
      <div style={styles.log} ref={logRef}>
        {messages.map((m, i) => (
          <div key={i} style={styles.msg(m.role)}>{m.content || "…"}</div>
        ))}
        {toolNote && <div style={styles.tool}>{toolNote}</div>}
      </div>
      <div style={styles.row}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about ticket prices, or book a flight…"
        />
        <button style={styles.btn} onClick={send} disabled={busy}>
          {busy ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}