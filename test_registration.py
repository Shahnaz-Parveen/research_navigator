from app import app, db
from models import User

def simulate_registration(email, name, password):
    with app.app_context():
        # Check if user exists
        if User.query.filter_by(email=email).first():
            print(f"User {email} already exists.")
            return

        # Create new user
        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Verify creation
        saved_user = User.query.filter_by(email=email).first()
        if saved_user and saved_user.check_password(password):
            print(f"SUCCESS: User '{name}' ({email}) registered and password verified.")
        else:
            print("FAILURE: User was not saved correctly.")

if __name__ == "__main__":
    simulate_registration("new_user@example.com", "New User", "securepass")
