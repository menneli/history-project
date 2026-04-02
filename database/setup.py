from database.db import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"📊 Tables in database: {tables}")

if not tables:
    print("❌ No tables found! Run init_db() first.")
elif 'songs' in tables and 'events' in tables:
    print("✅ All tables present!")