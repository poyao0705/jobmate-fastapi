import sys
import os

# Add current directory to sys.path so we can import app
sys.path.append(os.getcwd())

from sqlalchemy import inspect
from app.db.database import engine

def inspect_db():
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        if not table_names:
            print("No tables found in the database.")
            return

        print(f"Found {len(table_names)} tables:")
        for table_name in table_names:
            print(f"\nTable: {table_name}")
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f"  - {column['name']} ({column['type']})")
    except Exception as e:
        print(f"Error inspecting database: {e}")

if __name__ == "__main__":
    inspect_db()
