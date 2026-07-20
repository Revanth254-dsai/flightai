import uuid, urllib.parse, requests
from openai import OpenAI
from app.config import GROQ_API_KEY, BASE_URL, TTS_MODEL, MEDIA_DIR

client = OpenAI(api_key=GROQ_API_KEY or "missing", base_url=BASE_URL)

def speech(text: str) -> str | None:
    try:
        r = client.audio.speech.create(model=TTS_MODEL, voice="hannah",
                                       input=text[:600], response_format="wav")
        name = f"{uuid.uuid4().hex}.wav"
        r.write_to_file(MEDIA_DIR / name)
        return name
    except Exception as e:
        print("TTS failed:", e); return None

def city_image(city: str) -> str | None:
    try:
        prompt = f"A vacation in {city}, tourist spots, vibrant pop-art style"
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=768&height=768&nologo=true"
        name = f"{uuid.uuid4().hex}.png"
        (MEDIA_DIR / name).write_bytes(requests.get(url, timeout=90).content)
        return name
    except Exception as e:
        print("Image failed:", e); return None