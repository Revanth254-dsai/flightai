import { mediaUrl } from "../api.js";

const styles = {
  box: { flex: 1, background: "#181c2e", borderRadius: 12, padding: 16,
         display: "flex", flexDirection: "column", gap: 12, height: "75vh" },
  img: { width: "100%", borderRadius: 10 },
  placeholder: { color: "#9aa0b5", textAlign: "center", marginTop: 40 },
};

export default function MediaPanel({ media }) {
  const audio = mediaUrl(media.audio_url);
  const image = mediaUrl(media.image_url);

  return (
    <div style={styles.box}>
      <h3 style={{ margin: 0 }}>Destination</h3>
      {image ? <img src={image} style={styles.img} alt="destination" />
             : <div style={styles.placeholder}>Ask about a city to see it here 🌆</div>}
      {audio && <audio key={audio} src={audio} controls autoPlay style={{ width: "100%" }} />}
    </div>
  );
}