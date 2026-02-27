import sys
import os

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Add is_deleted column to orders table
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE orders ADD COLUMN is_deleted BOOLEAN DEFAULT 0"))
            conn.commit()
        print("Successfully added is_deleted column to orders table!")
    except Exception as e:
        print(f"Error adding column: {e}")
        # If it already exists, that's fine too
