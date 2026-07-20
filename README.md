# ✈️ FlightAI — Agentic Airline Assistant

Full-stack AI customer-support assistant with **streaming LLM tool calling**, text-to-speech, and image generation. React frontend consumes a Server-Sent Events stream from a FastAPI backend running an agentic loop on Groq.

## Demo
- **Live:** _coming soon_
- Ask: *"How much is a ticket to Tokyo?"* → watch the agent call the pricing tool, stream its reply, speak it aloud, and render city art.
- Say: *"Book me a flight to Paris, my name is X"* → the agent chains tools and writes a booking to the database.

## Architecture

```
React (Vite) ──POST /api/chat──▶ FastAPI ──▶ Groq (llama-3.3-70b, function calling)
     ◀──SSE: token / tool / media events──┘        │
                                          ┌────────┴────────┐
                                     SQLite tools      Orpheus TTS +
                                  (prices, bookings)   Pollinations images
                                                       (run concurrently)
```

**SSE event protocol**
```
data: {"type":"token","content":"The"}
data: {"type":"tool","name":"get_ticket_price","arguments":"{\"destination_city\":\"Tokyo\"}"}
data: {"type":"media","audio_url":"/api/media/x.wav","image_url":"/api/media/y.png"}
data: {"type":"done"}
```

## Key engineering details
- **Streaming agentic loop** — accumulates tool-call deltas across stream chunks, executes tools, feeds results back, loops until the model answers (capped rounds to prevent infinite loops)
- **SSE over fetch + ReadableStream** on the frontend (native EventSource can't POST)
- **Concurrent media generation** — TTS and image run in parallel via `asyncio` after the reply completes
- **Tool registry pattern** — add a new tool by writing one function + one schema
- Pydantic validation, CORS, path-traversal protection on media serving

## Stack
FastAPI · SQLAlchemy · Pydantic v2 · OpenAI SDK (Groq) · React 18 · Vite

## Run locally
```bash
# backend
cd backend
python -m venv .venv && .venv/Scripts/activate   # source .venv/bin/activate on Linux/Mac
pip install -r requirements.txt
echo GROQ_API_KEY=gsk_... > .env
python seed.py
uvicorn app.main:app --reload --port 8000

# frontend (second terminal)
cd frontend
npm install
npm run dev        # http://localhost:5173
```

## API
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/chat` | SSE stream of the agentic conversation |
| GET/POST | `/api/prices` | List / upsert ticket prices |
| GET | `/api/bookings` | Bookings made by the agent |
| GET | `/api/media/{file}` | Generated audio & images |

## Roadmap
- [ ] JWT auth + admin dashboard for prices
- [ ] Postgres + S3 for persistent storage
- [ ] Dockerize + CI