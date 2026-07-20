import json
from app.db import Session, Price, Booking

def get_ticket_price(destination_city: str) -> str:
    with Session() as db:
        row = db.get(Price, destination_city.lower())
    return f"A return ticket to {destination_city} costs ${row.price:.0f}" if row \
        else f"No price data for {destination_city}"

def book_flight(destination_city: str, passenger_name: str) -> str:
    with Session() as db:
        row = db.get(Price, destination_city.lower())
        if not row:
            return f"Cannot book: no flights to {destination_city}"
        b = Booking(city=row.city, passenger_name=passenger_name, price=row.price)
        db.add(b); db.commit(); db.refresh(b)
    return f"Booking confirmed! Ref #{b.id}: {passenger_name} -> {destination_city} at ${b.price:.0f}"

REGISTRY = {"get_ticket_price": get_ticket_price, "book_flight": book_flight}

SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_ticket_price",
        "description": "Get the price of a return ticket to the destination city.",
        "parameters": {"type": "object",
            "properties": {"destination_city": {"type": "string"}},
            "required": ["destination_city"]}}},
    {"type": "function", "function": {
        "name": "book_flight",
        "description": "Book a flight. Only after the customer confirms and gives their name.",
        "parameters": {"type": "object",
            "properties": {"destination_city": {"type": "string"},
                           "passenger_name": {"type": "string"}},
            "required": ["destination_city", "passenger_name"]}}},
]

def execute(name: str, args_json: str) -> str:
    try:
        return REGISTRY[name](**json.loads(args_json or "{}"))
    except Exception as e:
        return f"Tool {name} failed: {e}"