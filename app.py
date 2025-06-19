# app.py
from flask import Flask, redirect, url_for, session
from config import Config
from extensions import db            
from werkzeug.security import generate_password_hash

# -------------------------------------------------
# 1) Création de l'application Flask
# -------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# -------------------------------------------------
# 2) Initialisation de SQLAlchemy
# -------------------------------------------------
db.init_app(app)

# -------------------------------------------------
# 3) Enregistrement des blueprints
#    (on les importe **après** que 'app' et 'db' soient prêts)
# -------------------------------------------------
from auth import auth_bp
from cv import cv_bp
from interview import interview_bp
from admin import admin_bp
from jobs import jobs_bp

app.register_blueprint(auth_bp,      url_prefix="/auth")
app.register_blueprint(cv_bp,        url_prefix="/cv")
app.register_blueprint(interview_bp, url_prefix="/interview")
app.register_blueprint(admin_bp,     url_prefix="/admin")
app.register_blueprint(jobs_bp)      # /jobs

# -------------------------------------------------
# 4) Route racine : redirige selon le statut de connexion et le rôle
# -------------------------------------------------
@app.route("/")
def index():
    # Si l'utilisateur est connecté
    if session.get('user_id'):
        # Si c'est un admin, rediriger vers admin/jobs
        if session.get('is_admin'):
            return redirect(url_for("admin.jobs"))
        # Sinon, rediriger vers /jobs (utilisateur normal)
        else:
            return redirect(url_for("jobs.show_jobs"))
    # Si pas connecté, rediriger vers login
    else:
        return redirect(url_for("auth.login"))

# -------------------------------------------------
# 5) Création des tables + admin par défaut
# -------------------------------------------------
with app.app_context():
    from models import User, Job, CV, ChatbotSession, Decision  # import ici, db déjà initialisé
    db.create_all()

    # Créer l'admin s'il n'existe pas
    if not User.query.filter_by(email="admin@admin.com").first():
        admin = User(
            email="admin@admin.com",
            password_hash=generate_password_hash("admin"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin créé : admin@admin.com | admin")

# -------------------------------------------------
# 6) Lancement
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
