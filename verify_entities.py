from app import app, db
from models import Document, Entity

def verify():
    with app.app_context():
        doc = Document.query.first()
        if not doc:
            print("No documents found.")
            return
        
        print(f"Document: {doc.title}")
        print(f"Abstract snippet: {doc.abstract[:100]}...")
        print(f"Entities ({doc.entities.count()}):")
        for ent in doc.entities:
            print(f" - [{ent.label}] {ent.text}")

if __name__ == "__main__":
    verify()
