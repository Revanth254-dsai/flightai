import asyncio, json
from openai import OpenAI
from app.config import GROQ_API_KEY, BASE_URL, CHAT_MODEL, SYSTEM_MESSAGE
from app import tools, media

client = OpenAI(api_key=GROQ_API_KEY or "missing", base_url=BASE_URL)
FINAL = "__final__"
SENTINEL = object()

def _stream_once(messages):
    """Yield token strings, then a final ('__final__', content, tool_calls) tuple."""
    stream = client.chat.completions.create(model=CHAT_MODEL, messages=messages,
                                            tools=tools.SCHEMAS, stream=True)
    content, calls = [], {}
    for chunk in stream:
        if not chunk.choices: continue
        d = chunk.choices[0].delta
        if d.content:
            content.append(d.content)
            yield d.content
        for tc in d.tool_calls or []:
            c = calls.setdefault(tc.index, {"id": "", "name": "", "args": ""})
            if tc.id: c["id"] = tc.id
            if tc.function.name: c["name"] = tc.function.name
            if tc.function.arguments: c["args"] += tc.function.arguments
    yield (FINAL, "".join(content), [calls[i] for i in sorted(calls)])

async def run_agent(history):
    messages = [{"role": "system", "content": SYSTEM_MESSAGE}] + history
    cities, reply = [], ""
    try:
        for _ in range(5):                                  # max tool rounds
            gen = _stream_once(messages)
            calls = []
            while True:
                item = await asyncio.to_thread(next, gen, SENTINEL)
                if item is SENTINEL:
                    break
                if isinstance(item, tuple) and item[0] == FINAL:
                    reply, calls = item[1], item[2]
                else:
                    yield {"type": "token", "content": item}
            if not calls:
                break
            messages.append({"role": "assistant", "content": reply or None,
                "tool_calls": [{"id": c["id"], "type": "function",
                    "function": {"name": c["name"], "arguments": c["args"]}} for c in calls]})
            for c in calls:
                yield {"type": "tool", "name": c["name"], "arguments": c["args"]}
                result = await asyncio.to_thread(tools.execute, c["name"], c["args"])
                city = json.loads(c["args"] or "{}").get("destination_city")
                if city: cities.append(city)
                messages.append({"role": "tool", "content": result, "tool_call_id": c["id"]})

        audio = asyncio.create_task(asyncio.to_thread(media.speech, reply)) if reply else None
        image = asyncio.create_task(asyncio.to_thread(media.city_image, cities[0])) if cities else None
        audio_file = await audio if audio else None
        image_file = await image if image else None
        yield {"type": "media",
               "audio_url": f"/api/media/{audio_file}" if audio_file else None,
               "image_url": f"/api/media/{image_file}" if image_file else None}
        yield {"type": "done"}
    except Exception as e:
        yield {"type": "error", "detail": str(e)}