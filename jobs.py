# jobs.py
from flask import Blueprint, render_template, redirect, url_for, session, flash
from models import Job                        
from app import db     


jobs_bp = Blueprint("jobs", __name__, template_folder="templates")

@jobs_bp.route("/jobs")
def show_jobs():
    """Liste publique de tous les jobs."""
    jobs = Job.query.order_by(Job.date_created.desc()).all()
    return render_template("jobs.html", jobs=jobs)

@jobs_bp.route("/jobs/<int:job_id>/apply", methods=["GET", "POST"])
def apply_job(job_id):
    """L’utilisateur choisit un job ; on stocke la description puis on redirige vers l’upload CV."""
    job = Job.query.get_or_404(job_id)
    session["selected_job_description"] = job.description
    flash(f"Vous postulez pour : {job.title}")
    return redirect(url_for("cv.upload_cv"))
