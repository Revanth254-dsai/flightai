import { useState } from "react";
import Chat from "./components/Chat.jsx";
import MediaPanel from "./components/MediaPanel.jsx";

const styles = {
  page: { fontFamily: "system-ui, sans-serif", background: "#0f1220",
          color: "#e8e8f0", minHeight: "100vh", padding: 20 },
  title: { textAlign: "center", margin: "0 0 16px" },
  layout: { display: "flex", gap: 16, maxWidth: 1100, margin: "0 auto" },
};

export default function App() {
  const [media, setMedia] = useState({ audio_url: null, image_url: null });

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>✈️ FlightAI</h1>
      <div style={styles.layout}>
        <Chat onMedia={setMedia} />
        <MediaPanel media={media} />
      </div>
    </div>
  );
}