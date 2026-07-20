from app.db import Session, Price

with Session() as db:
    for city, price in {"london": 799, "paris": 899, "tokyo": 1420,
                        "sydney": 2999, "berlin": 499}.items():
        row = db.get(Price, city) or Price(city=city)
        row.price = price
        db.add(row)
    db.commit()
print("Seeded.")