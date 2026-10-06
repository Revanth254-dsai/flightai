import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent          # .../flightai/backend
load_dotenv(ROOT / ".env", override=True)               # load backend/.env explicitly

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
BASE_URL = "https://api.groq.com/openai/v1"
CHAT_MODEL = "openai/gpt-oss-120b"                      # llama-3.3-70b-versatile was retired by Groq
TTS_MODEL = "canopylabs/orpheus-v1-english"

MEDIA_DIR = ROOT / "media"
MEDIA_DIR.mkdir(exist_ok=True)


SYSTEM_MESSAGE = """You are a helpful assistant for an Airline called FlightAI, operating flights from Tirupati, India.
All prices are in Indian Rupees (₹).
Give short, courteous answers, no more than 1 sentence.
Always be accurate. If you don't know the answer, say so.
Use get_ticket_price whenever a customer asks about a price."""