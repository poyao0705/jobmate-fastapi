import sys
import os
import asyncio

# Add current directory to sys.path so we can import app
sys.path.append(os.getcwd())

from sqlalchemy import inspect
from app.db.database import engine


def get_inspector(conn):
    return inspect(conn)


async def inspect_db():
    try:
        async with engine.connect() as conn:
            table_names = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )

            if not table_names:
                print("No tables found in the database.")
                return

            print(f"Found {len(table_names)} tables:")
            for table_name in table_names:
                print(f"\nTable: {table_name}")
                columns = await conn.run_sync(
                    lambda sync_conn: inspect(sync_conn).get_columns(table_name)
                )
                for column in columns:
                    print(f"  - {column['name']} ({column['type']})")
    except Exception as e:
        print(f"Error inspecting database: {e}")


if __name__ == "__main__":
    asyncio.run(inspect_db())
