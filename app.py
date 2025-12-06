from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from database import db
from models import User, Document, Entity
from datetime import datetime
import nlp_engine
import pickle
import os
from search_engine import SearchEngine

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Ensure database tables exist on startup
with app.app_context():
    db.create_all()

login = LoginManager(app)
login.login_view = 'login'

# Global singleton
_search_engine_instance = None

def get_search_engine():
    global _search_engine_instance
    if _search_engine_instance is None:
        try:
            print("Initializing Search Engine (Lazy Load)...")
            from search_engine import SearchEngine
            engine = SearchEngine()
            # Create app context to access DB
            with app.app_context():
                docs = Document.query.all()
                if docs:
                    engine.rebuild_index(docs)
            _search_engine_instance = engine
            print("Search Engine Ready.")
        except Exception as e:
            print(f"Failed to initialize search engine: {e}")
            _search_engine_instance = None
    return _search_engine_instance

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
            
        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    query = request.args.get('q')
    engine = get_search_engine()
    
    if query and engine:
        results = engine.search(query) # List of (id, score)
        if not results:
            documents = []
            flash(f'No semantic matches found for "{query}".')
        else:
            doc_ids = [r[0] for r in results]
            documents = []
            for doc_id in doc_ids:
                d = db.session.get(Document, doc_id)
                if d: documents.append(d)
    else:
        documents = Document.query.order_by(Document.ingestion_date.desc()).limit(20).all()
        
    return render_template('dashboard.html', documents=documents)

@app.route('/document/<int:id>')
@login_required
def document_detail(id):
    doc = db.session.get(Document, id)
    if not doc:
        return redirect(url_for('dashboard'))
        
    related_docs = []
    engine = get_search_engine()
    if engine:
        similar = engine.find_similar(id, k=5)
        for sim_id, score in similar:
            d = db.session.get(Document, sim_id)
            if d:
                related_docs.append(d)
                
    # Calculate Word Frequency
    from collections import Counter
    import re
    words = re.findall(r'\w+', doc.abstract.lower())
    stopwords = set(['the', 'and', 'of', 'to', 'in', 'a', 'is', 'for', 'that', 'on', 'with', 'as', 'are', 'by', 'it', 'an', 'be', 'this', 'from', 'at', 'which', 'or', 'not', 'but', 'can', 'has', 'have', 'we', 'our', 'their', 'all', 'more', 'one', 'new', 'used', 'using', 'also', 'paper', 'results', 'data', 'model', 'based', 'such', 'these'])
    filtered_words = [w for w in words if w not in stopwords and len(w) > 2 and not w.isdigit()]
    word_counts = Counter(filtered_words).most_common(10) # List of (word, count)
    
    # Prepare data for Chart.js
    chart_labels = [w[0] for w in word_counts]
    chart_data = [w[1] for w in word_counts]
    
    # Generate Summary
    try:
        summary = nlp_engine.generate_summary(doc.abstract)
    except Exception as e:
        summary = "Summary generation unavailable."

    return render_template('document_detail.html', doc=doc, related_docs=related_docs, chart_labels=chart_labels, chart_data=chart_data, summary=summary)

@app.route('/admin')
@login_required
def admin_dashboard():
    # In a real app, check for admin role. For now, open to all logged in users.
    total_papers = Document.query.count()
    total_users = User.query.count()
    total_entities = Entity.query.count()
    
    return render_template('admin_dashboard.html', total_papers=total_papers, total_users=total_users, total_entities=total_entities)

@app.route('/add-paper', methods=['GET', 'POST'])
@login_required
def add_paper():
    from werkzeug.utils import secure_filename
    from models import Entity # Import here to be available for all blocks
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'manual':
            title = request.form['title']
            title = title[:295] + "..." if len(title) > 300 else title
            abstract = request.form['abstract']
            source_url = request.form.get('source_url') or '-'
            date_str = request.form.get('published_date')
            
            published_date = datetime.utcnow()
            if date_str:
                try:
                    published_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    pass
            
            doc = Document(
                title=title,
                abstract=abstract,
                source_url=source_url,
                published_date=published_date
            )
            db.session.add(doc)
            db.session.commit() # Commit first to get ID
            
            # Indexing
            engine = get_search_engine()
            if engine:
                try:
                    embedding = engine.add_document(doc.id, abstract)
                    doc.embedding = pickle.dumps(embedding)
                except Exception as e:
                    print(f"Indexing error: {e}")
            
            # NER
            try:
                extracted = nlp_engine.extract_entities(abstract)
                for text, label in extracted:
                    safe_text = text[:95] + "..." if len(text) > 100 else text
                    entity = Entity(text=safe_text, label=label, document=doc)
                    db.session.add(entity)
            except Exception as e:
                print(f"NER error: {e}")
                
            db.session.commit()
            flash('Paper added successfully! Entities extracted.')
            return redirect(url_for('document_detail', id=doc.id))
            
        elif action == 'ingest':
            query = request.form['query']
            max_results = int(request.form['max_results'])
            
            from ingestion.arxiv_fetcher import fetch_arxiv_papers
            try:
                fetch_arxiv_papers(query=query, max_results=max_results)
                flash(f'Successfully fetched papers for "{query}". Embeddings will be generated on next restart or search.')
            except Exception as e:
                flash(f"Error fetching papers: {e}")
            
            return redirect(url_for('dashboard'))

        elif action == 'upload':
            file = request.files['file']
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    text = ""
                    for page in reader.pages[:5]:
                        text += (page.extract_text() or "") + "\n"
                    
                    lines = [l for l in text.split('\n') if l.strip()]
                    raw_title = lines[0].strip() if lines else "Uploaded PDF"
                    title = raw_title[:295] + "..." if len(raw_title) > 300 else raw_title
                    
                    abstract = text[:5000] # Increased limit but still safe
                    
                    doc = Document(
                        title=title,
                        abstract=abstract,
                        
                        source_url=url_for('static', filename=f'uploads/{filename}'),
                        published_date=datetime.utcnow()
                    )
                    db.session.add(doc)
                    db.session.commit()
                    
                    engine = get_search_engine()
                    if engine:
                        try:
                            embedding = engine.add_document(doc.id, abstract)
                            doc.embedding = pickle.dumps(embedding)
                        except Exception as e:
                            print(f"Indexing error: {e}")
                    
                    try:
                        extracted = nlp_engine.extract_entities(abstract)
                        for text_ent, label in extracted:
                            safe_text = text_ent[:95] + "..." if len(text_ent) > 100 else text_ent
                            entity = Entity(text=safe_text, label=label, document=doc)
                            db.session.add(entity)
                    except Exception as e:
                        print(f"NER error: {e}")
                        
                    db.session.commit()
                    flash(f'PDF "{filename}" uploaded and processed successfully!')
                    return redirect(url_for('document_detail', id=doc.id))
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    flash(f'Error processing PDF: {str(e)}')
                    return redirect(url_for('add_paper'))
            
    return render_template('add_paper.html')

@app.route('/delete-paper/<int:id>', methods=['POST'])
@login_required
def delete_paper(id):
    doc = db.session.get(Document, id)
    if not doc:
        flash('Document not found.')
        return redirect(url_for('dashboard'))
    
    from models import Entity
    Entity.query.filter_by(doc_id=id).delete()
    
    db.session.delete(doc)
    db.session.commit()
    flash('Paper deleted successfully.')
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from werkzeug.utils import secure_filename
    
    if request.method == 'POST':
        new_name = request.form.get('name')
        if new_name:
            current_user.name = new_name
            
        new_bio = request.form.get('bio')
        if new_bio:
            current_user.bio = new_bio
            
        file = request.files.get('profile_image')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_ext = os.path.splitext(filename)[1]
            new_filename = f"user_{current_user.id}_{int(datetime.utcnow().timestamp())}{file_ext}"
            
            upload_folder = os.path.join(app.root_path, 'static', 'profile_pics')
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, new_filename)
            file.save(file_path)
            current_user.profile_image = new_filename

        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
        
    image_file = url_for('static', filename='profile_pics/' + (current_user.profile_image or 'default.jpg'))
    return render_template('profile.html', image_file=image_file)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/graph')
@login_required
def graph():
    return render_template('graph.html')

@app.route('/graph-data')
@login_required
def graph_data():
    documents = Document.query.all()
    
    nodes = []
    edges = []
    
    # Track added concepts to merge them (Concept Text -> Node ID)
    concept_map = {} 
    concept_counter = 0
    
    for doc in documents:
        # Add Paper Node
        doc_node_id = f"doc_{doc.id}"
        # Truncate title for label
        label = doc.title[:30] + "..." if len(doc.title) > 30 else doc.title
        nodes.append({
            "id": doc_node_id,
            "label": label,
            "group": "paper",
            "title": doc.title  # Tooltip
        })
        
        # Add Entities
        for entity in doc.entities:
            # key = (entity.text.lower(), entity.label)
            # Use raw text for display but lower for merging
            key = entity.text.lower()
            
            if key not in concept_map:
                concept_id = f"conc_{concept_counter}"
                concept_counter += 1
                concept_map[key] = concept_id
                
                nodes.append({
                    "id": concept_id,
                    "label": entity.text,
                    "group": "entity", # We could use entity.label for color groups later
                    "color": "#e0e7ff" # Light indigo default
                })
            else:
                concept_id = concept_map[key]
                
            # Add Edge
            edges.append({
                "from": doc_node_id,
                "to": concept_id
            })
            
    return {"nodes": nodes, "edges": edges}

@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    from chatbot import ResearchNavigatorBot
    
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return {"response": "Please say something!"}
        
    try:
        engine = get_search_engine()
        bot = ResearchNavigatorBot(engine)
        
        response = bot.process_message(message)
        return {"response": response}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"response": "I'm having a little trouble thinking right now. Please try again. 🤕"}, 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
