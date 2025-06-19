from flask import Blueprint, render_template, redirect, request, url_for, session, flash
from models import Job, Decision, User
from app import db
from sqlalchemy import desc

admin_bp = Blueprint('admin', __name__, template_folder="templates/admin")

# Vérification admin (décorateur simple)
def admin_required(f):
    def wrap(*args, **kwargs):
        if session.get("is_admin"):
            return f(*args, **kwargs)
        flash("Vous devez être administrateur pour accéder.")
        return redirect(url_for('auth.login'))
    wrap.__name__ = f.__name__
    return wrap

@admin_bp.route('/jobs')
@admin_required
def jobs():
    jobs = Job.query.order_by(Job.date_created.desc()).all()
    return render_template('admin/jobs.html', jobs=jobs)

@admin_bp.route('/jobs/create', methods=["GET", "POST"])
@admin_required
def create_job():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        job = Job(title=title, description=description)
        db.session.add(job)
        db.session.commit()
        flash("Job créé avec succès.")
        return redirect(url_for('admin.jobs'))
    return render_template('admin/create_job.html')

@admin_bp.route('/jobs/edit/<int:job_id>', methods=["GET", "POST"])
@admin_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if request.method == "POST":
        job.title = request.form['title']
        job.description = request.form['description']
        db.session.commit()
        flash("Job modifié avec succès.")
        return redirect(url_for('admin.jobs'))
    return render_template('admin/edit_job.html', job=job)

@admin_bp.route('/jobs/delete/<int:job_id>')
@admin_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Job supprimé avec succès.")
    return redirect(url_for('admin.jobs'))

@admin_bp.route('/applications')
@admin_required
def applications():
    # Fetch applications with user information using join
    applications = db.session.query(
        Decision.id,
        Decision.total_score,
        Decision.status,
        Decision.decision_date,
        User.email,
        User.id.label('user_id')
    ).join(User, Decision.user_id == User.id).order_by(desc(Decision.decision_date)).all()
    
    return render_template('admin/applications.html', applications=applications)
