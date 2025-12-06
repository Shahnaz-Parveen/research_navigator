from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        print("Migrating database within app context...")
        
        # Add profile_image column
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE user ADD COLUMN profile_image VARCHAR(120) DEFAULT 'default.jpg'"))
                conn.commit()
            print("Added profile_image column.")
        except Exception as e:
            print(f"profile_image column might already exist or error: {e}")

        # Add bio column
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE user ADD COLUMN bio TEXT"))
                conn.commit()
            print("Added bio column.")
        except Exception as e:
            print(f"bio column might already exist or error: {e}")

if __name__ == '__main__':
    migrate()
