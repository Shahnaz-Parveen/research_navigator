import arxiv
from app import app, db
from models import Document, Entity
from datetime import datetime
import nlp_engine

def fetch_arxiv_papers(query="artificial intelligence", max_results=10):
    """
    Fetches papers from ArXiv and saves them to the database.
    """
    print(f"Fetching {max_results} papers for query: {query}...")
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    count = 0
    with app.app_context():
        db.create_all()
        for result in client.results(search):
            try:
                # Check if exists
                if Document.query.filter_by(source_url=result.entry_id).first():
                    print(f"Skipping existing: {result.title[:30]}...")
                    continue

                title = result.title[:295] + "..." if len(result.title) > 300 else result.title
                # Truncate abstract to safe length (5000 chars)
                abstract = result.summary[:4995] + "..." if len(result.summary) > 5000 else result.summary
                
                doc = Document(
                    title=title,
                    abstract=abstract,
                    source_url=result.entry_id,
                    published_date=result.published
                )
                db.session.add(doc)
                db.session.flush()  # Get the ID before entities
                
                # Extract Entities
                try:
                    extracted = nlp_engine.extract_entities(abstract)
                    for text, label in extracted:
                        # Truncate entity text to 100 chars
                        safe_text = text[:95] + "..." if len(text) > 100 else text
                        entity = Entity(text=safe_text, label=label, document=doc)
                        db.session.add(entity)
                except Exception as e:
                    print(f"Entity extraction failed: {e}")
                    
                count += 1
                
            except Exception as e:
                print(f"Failed to process paper '{result.title[:30]}...': {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f"Successfully ingested {count} new papers.")
        except Exception as e:
            print(f"Commit failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    # Default ingestion for testing
    fetch_arxiv_papers()
