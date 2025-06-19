# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import db

auth_bp = Blueprint("auth", __name__, template_folder="templates/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"]   = user.id
            session["user_email"]= user.email
            session["is_admin"]  = user.is_admin
            flash("Connexion réussie.", "success")
            # L’admin peut aller direct en /admin/jobs
            if user.is_admin:
                return redirect(url_for("admin.jobs"))
            else:
                return redirect(url_for("jobs.show_jobs"))

        flash("Email ou mot de passe invalide.", "danger")
    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Cet email existe déjà.", "warning")
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(email=email, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash("Inscription réussie ! Vous pouvez vous connecter.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("auth.login"))
