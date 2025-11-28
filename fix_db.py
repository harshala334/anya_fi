from app.db.database import get_db_context
from sqlalchemy import text

def add_column():
    print("Adding is_essential column to transactions table...")
    with get_db_context() as db:
        try:
            db.execute(text("ALTER TABLE transactions ADD COLUMN is_essential BOOLEAN DEFAULT FALSE"))
            db.commit()
            print("✅ Column added successfully!")
        except Exception as e:
            print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_column()
