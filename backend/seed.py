from app.db import Session, Price

with Session() as db:
    for city, price in {"delhi": 9500, "bengaluru": 4200, "chennai": 3800,
                        "hyderabad": 4500, "pune": 7200, "kochi": 6800,
                        "vizag": 5500, "mumbai": 8200, "goa": 7500,
                        "kolkata": 9800}.items():
        row = db.get(Price, city) or Price(city=city)
        row.price = price
        db.add(row)
    db.commit()
print("Seeded.")