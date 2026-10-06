import time, uuid, urllib.parse, requests
from openai import OpenAI
from app.config import GROQ_API_KEY, POLLINATIONS_API_KEY, BASE_URL, TTS_MODEL, MEDIA_DIR

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


def _image_request(prompt: str) -> tuple[str, dict]:
    """New authenticated endpoint if a key is set, else the legacy anonymous one."""
    q = urllib.parse.quote(prompt)
    if POLLINATIONS_API_KEY:
        url = f"https://gen.pollinations.ai/image/{q}?model=flux&width=768&height=768"
        return url, {"Authorization": f"Bearer {POLLINATIONS_API_KEY}"}
    return f"https://image.pollinations.ai/prompt/{q}?width=768&height=768&nologo=true", {}


def city_image(city: str) -> str | None:
    prompt = f"A vacation in {city}, tourist spots, vibrant pop-art style"
    url, headers = _image_request(prompt)

    for attempt in range(2):
        try:
            r = requests.get(url, headers=headers, timeout=90)
            ctype = r.headers.get("content-type", "")

            # Only save the response if it is actually an image.
            if r.status_code == 200 and ctype.startswith("image/"):
                ext = "jpg" if "jpeg" in ctype else ctype.split("/")[1].split(";")[0]
                name = f"{uuid.uuid4().hex}.{ext}"
                (MEDIA_DIR / name).write_bytes(r.content)
                return name

            print(f"Image failed: HTTP {r.status_code} {ctype} {r.text[:200]}")
            if r.status_code == 402 and not POLLINATIONS_API_KEY:
                print("Hint: set POLLINATIONS_API_KEY in backend/.env (enter.pollinations.ai)")

            # Rate-limited: wait once and retry.
            if r.status_code == 429 and attempt == 0:
                time.sleep(16)
                continue
            return None
        except Exception as e:
            print("Image failed:", e)
            return None
    return None