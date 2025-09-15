from app.db import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text("SELECT 1"))
    print("DB connected:", result.scalar())
finally:
    db.close()
