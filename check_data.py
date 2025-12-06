from app import app, db
from models import Document, User

with app.app_context():
    print("=" * 50)
    print("DATABASE CHECK")
    print("=" * 50)
    
    # Check documents
    docs = Document.query.all()
    print(f"\nTotal Documents: {len(docs)}")
    if docs:
        print("\nFirst 3 papers:")
        for i, doc in enumerate(docs[:3], 1):
            print(f"  {i}. {doc.title[:60]}")
    
    # Check users
    users = User.query.all()
    print(f"\nTotal Users: {len(users)}")
    if users:
        print("\nRegistered users:")
        for user in users:
            print(f"  - {user.email}")
    else:
        print("\nWARNING: No users registered!")
        print("  You need to register an account to see the dashboard.")
    
    print("\n" + "=" * 50)
