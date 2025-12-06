from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        print("Migrating database for embeddings...")
        
        # Add embedding column
        try:
            with db.engine.connect() as conn:
                # pickle type usually maps to BLOB in SQLite
                conn.execute(text("ALTER TABLE document ADD COLUMN embedding BLOB"))
                conn.commit()
            print("Added embedding column.")
        except Exception as e:
            print(f"embedding column might already exist or error: {e}")

if __name__ == '__main__':
    migrate()
