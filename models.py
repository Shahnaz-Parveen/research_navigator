from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image = db.Column(db.String(120), default='default.jpg')
    bio = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(500))
    published_date = db.Column(db.DateTime)
    ingestion_date = db.Column(db.DateTime, default=datetime.utcnow)
    embedding = db.Column(db.PickleType) # Stores the vector as a numpy array
    
    entities = db.relationship('Entity', backref='document', lazy='dynamic')

class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)

