import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field

from app.config import MEDIA_DIR
from app.db import Session, Price, Booking
from app.llm import run_agent

app = FastAPI(title="FlightAI API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])

class Msg(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str

class ChatReq(BaseModel):
    messages: list[Msg] = Field(min_length=1)

class PriceIn(BaseModel):
    city: str = Field(min_length=1)
    price: float = Field(gt=0)

@app.post("/api/chat")
async def chat(req: ChatReq):
    async def events():
        async for e in run_agent([m.model_dump() for m in req.messages]):
            yield f"data: {json.dumps(e)}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")

@app.get("/api/prices")
def prices():
    with Session() as db:
        return [{"city": p.city, "price": p.price} for p in db.query(Price).order_by(Price.city)]

@app.post("/api/prices", status_code=201)
def upsert(p: PriceIn):
    with Session() as db:
        row = db.get(Price, p.city.lower()) or Price(city=p.city.lower())
        row.price = p.price
        db.add(row); db.commit()
        return {"city": row.city, "price": row.price}

@app.get("/api/bookings")
def bookings():
    with Session() as db:
        return [{"id": b.id, "city": b.city, "passenger_name": b.passenger_name,
                 "price": b.price, "created_at": str(b.created_at)}
                for b in db.query(Booking).order_by(Booking.id.desc())]

@app.get("/api/media/{name}")
def media_file(name: str):
    path = (MEDIA_DIR / name).resolve()
    if not path.is_relative_to(MEDIA_DIR.resolve()) or not path.is_file():
        raise HTTPException(404)
    return FileResponse(path)

@app.get("/api/health")
def health():
    return {"status": "ok"}