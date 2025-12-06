from app import app, db
from models import User

def create_user():
    with app.app_context():
        # Check if user exists
        u = User.query.filter_by(email="test@example.com").first()
        if u:
            print("User already exists!")
            return

        user = User(email="test@example.com", name="Test User")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        print("User 'test@example.com' created successfully.")

if __name__ == "__main__":
    create_user()
