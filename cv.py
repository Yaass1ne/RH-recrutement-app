# cv.py ──────────────────────────────────────────────────────────────
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import fitz, re, torch, string
import spacy
from sentence_transformers import SentenceTransformer, util
from datetime import datetime
from app import db
from models import CV

cv_bp = Blueprint("cv", __name__, template_folder="templates/cv")

# ─────── NLP MODELS ───────
nlp   = spacy.load("fr_core_news_md")  # tokenizer / lemmatiseur
MODEL_PATH = "all-MiniLM-L6-v2"  

sbert = SentenceTransformer(
    MODEL_PATH,
    local_files_only=True             
)

DEFAULT_JOB_DESCRIPTION = """Développeur Python NLP avec 3+ ans d'expérience.
Compétences : Python, Flask, NLP (spaCy), MySQL, APIs REST.
Diplôme : Master/Bac+5 en Informatique."""

# ───────── helpers NLP ──────────
def preprocess(text: str):
    """Tokenise, lemmatise, enlève stop‑words & ponctuation, renvoie liste de lemmas."""
    doc = nlp(text.lower())
    return [
        tok.lemma_ for tok in doc
        if tok.is_alpha and not tok.is_stop and len(tok) > 2
    ]

def extract_degree(text: str):
    degs = {
        "master":  re.compile(r"\b(master|bac\s*\+?\s*5|ing[ée]nieur)\b", re.I),
        "licence": re.compile(r"\b(licence|bac\s*\+?\s*3)\b", re.I),
    }
    for lbl, pat in degs.items():
        if pat.search(text):
            return lbl
    return None

def extract_years(text: str):
    matches = re.findall(r"(\d{1,2})\s*(?:\+?\s*(?:ans?|years?))", text, flags=re.I)
    return max((int(n) for n in matches), default=0)

def dynamic_job_skills(tokens_job):
    """Considère comme « skill » tout token JOB qui est nom (NOUN/PROPN/VERB) et len>2."""
    doc = nlp(" ".join(tokens_job))
    return {
        tok.lemma_
        for tok in doc
        if tok.pos_ in {"NOUN", "PROPN", "VERB"} and len(tok) > 2
    }

# ───────── route /upload ──────────
@cv_bp.route("/upload", methods=["GET", "POST"])
def upload_cv():
    if "user_id" not in session:
        flash("Veuillez vous connecter pour continuer.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        pdf = request.files.get("cv_file")
        if not pdf or pdf.filename == "" or not pdf.filename.lower().endswith(".pdf"):
            flash("Veuillez choisir un fichier PDF.", "danger")
            return redirect(url_for("cv.upload_cv"))

        # Sauvegarde
        filename    = f"cv_{session['user_id']}_{int(datetime.now().timestamp())}.pdf"
        upload_path = f"uploads/{filename}"
        pdf.save(upload_path)

        # Extraction texte
        try:
            doc = fitz.open(upload_path)
            text = "".join(p.get_text("text") for p in doc)
            doc.close()
        except Exception:
            flash("Erreur de lecture PDF.", "danger")
            return redirect(url_for("cv.upload_cv"))

        if not text.strip():
            flash("Le CV est vide ou illisible.", "danger")
            return redirect(url_for("cv.upload_cv"))

        # ---------------  NLP  -------
        job_desc   = session.pop("selected_job_description", DEFAULT_JOB_DESCRIPTION)
        tokens_cv  = preprocess(text)
        tokens_job = preprocess(job_desc)

        skills_job = dynamic_job_skills(tokens_job)
        skills_cv  = {tok for tok in tokens_cv if tok in skills_job}

        # S1 : correspondance compétences (F1)
        tp   = len(skills_cv)
        prec = tp / len(skills_cv) if skills_cv else 0
        rec  = tp / len(skills_job) if skills_job else 0
        S1   = 0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)

        # S2 : diplôme
        S2 = 1.0 if extract_degree(text) == "master" else 0.0

        # S3 : années d’expérience
        cv_years = extract_years(text)
        S3 = min(cv_years / 3, 1.0)   # normalize (3 ans requis)

        # S4 : similarité sémantique (SBERT)
        emb_cv  = sbert.encode(" ".join(tokens_cv), convert_to_tensor=True, normalize_embeddings=True)
        emb_job = sbert.encode(job_desc, convert_to_tensor=True, normalize_embeddings=True)
        S4 = max(util.cos_sim(emb_cv, emb_job).item(), 0.0)

        # -----------  Score final -----------
        final = 0.35*S1 + 0.15*S2 + 0.15*S3 + 0.35*S4
        score_percent = round(final * 100, 2)

        # Sauvegarde BD
        db.session.add(CV(
            user_id=session["user_id"],
            path_to_cv=upload_path,
            extracted_text=text,
            filtered_score=score_percent
        ))
        db.session.commit()

        # Décision
        threshold = 55.0
        if score_percent < threshold:
            flash(f"Score {score_percent:.1f}% — profil non retenu.", "warning")
            return redirect(url_for("cv.upload_cv"))
        else:
            session["preselected"] = True
            flash(f"Score {score_percent:.1f}% — CV accepté ! Passez aux questions.", "success")
            return redirect(url_for("interview.questions"))

    return render_template("cv/upload.html")
