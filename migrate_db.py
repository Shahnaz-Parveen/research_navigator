import sqlite3

def migrate():
    print("Migrating database...")
    conn = sqlite3.connect('research_navigator.db')
    cursor = conn.cursor()
    
    try:
        # Add profile_image column
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN profile_image VARCHAR(120) DEFAULT 'default.jpg'")
            print("Added profile_image column.")
        except sqlite3.OperationalError as e:
            print(f"profile_image column might already exist: {e}")

        # Add bio column
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN bio TEXT")
            print("Added bio column.")
        except sqlite3.OperationalError as e:
            print(f"bio column might already exist: {e}")
            
        conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
