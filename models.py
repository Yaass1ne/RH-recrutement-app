# Modèles SQLAlchemy
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)

class CV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    path_to_cv = db.Column(db.String(255))
    extracted_text = db.Column(db.Text)
    filtered_score = db.Column(db.Float)

class ChatbotSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    question = db.Column(db.Text)
    response = db.Column(db.Text)
    score = db.Column(db.Integer)

class Decision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    total_score = db.Column(db.Integer)
    status = db.Column(db.String(20))
    decision_date = db.Column(db.DateTime, default=db.func.now())

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.now())
