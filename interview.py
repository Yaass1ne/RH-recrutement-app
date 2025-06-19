# interview.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import openai, os, re, smtplib, ssl
from email.message import EmailMessage
from app import db
from models import ChatbotSession, Decision, CV

interview_bp = Blueprint("interview", __name__, template_folder="templates/interview")

openai.api_key = os.getenv("OPENAI_API_KEY")

# Description de secours si aucune offre n’a été choisie
DEFAULT_JOB_DESCRIPTION = """Développeur Python NLP avec 3+ ans d'expérience.
Compétences : Python, Flask, NLP (spaCy), MySQL, APIs REST.
Diplôme : Master/Bac+5 en Informatique."""

# ────────────────────────────────────────────────────────────────
#   ROUTE /interview/questions
# ────────────────────────────────────────────────────────────────
@interview_bp.route("/questions", methods=["GET", "POST"])
def questions():
    # 1) Sécurité : utilisateur connecté ?
    if "user_id" not in session:
        flash("Veuillez vous connecter d'abord.", "warning")
        return redirect(url_for("auth.login"))

    # 2) Pré‑sélection via CV réussie ?
    if not session.get("preselected"):
        return redirect(url_for("cv.upload_cv"))

    # 3) Quelle description de poste employer ?
    job_description = session.get("selected_job_description", DEFAULT_JOB_DESCRIPTION)

    # ──────────── GET : générer les questions ────────────
    if request.method == "GET":
        if session.get("questions_list") is None:
            prompt = (
                "Tu es un recruteur technique. Génère 5 questions d'entretien "
                "pour évaluer un candidat sur le poste suivant :\n"
                f"{job_description}\n"
                "Liste uniquement les questions de manière concise :"
            )
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7,
                )
                questions_text = completion.choices[0].message.content.strip()
            except Exception:
                # Secours statique
                questions_text = (
                    "1. Parlez-moi de votre expérience avec Python et Flask.\n"
                    "2. Quelle est votre expérience avec les outils NLP – spaCy ?\n"
                    "3. Comment avez-vous utilisé MySQL dans vos projets ?\n"
                    "4. Décrivez une API REST que vous avez développée.\n"
                    "5. Pourquoi ce poste vous intéresse‑t‑il ?"
                )

            # Nettoyage « 1. … »
            questions = []
            for line in questions_text.splitlines():
                line = line.strip()
                if line and line[0].isdigit():
                    line = line.partition(" ")[2].lstrip()
                questions.append(line)
            session["questions_list"] = questions

        return render_template(
            "interview/questions.html",
            questions=session["questions_list"],
            job_title=session.get("selected_job_title")  # au cas où tu veux l’afficher
        )

    # ──────────── POST : traiter les réponses ────────────
    questions = session.get("questions_list")
    if not questions:
        return redirect(url_for("interview.questions"))

    total_score = 0
    responses_and_scores = []

    for idx, question in enumerate(questions):
        answer = request.form.get(f"answer{idx}")
        if not answer:
            score = 0
        else:
            eval_prompt = (
                f"Question : {question}\n"
                f"Réponse du candidat : {answer}\n\n"
                "Évalue la qualité de cette réponse sur 10 points "
                "(0 =minimal, 10 = excellent). "
                "Réponds uniquement par un score numérique."
            )
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": eval_prompt}],
                    max_tokens=10,
                    temperature=0.0,
                )
                score_str = completion.choices[0].message.content.strip()
                score = int(re.search(r"\d+", score_str).group()) if re.search(r"\d+", score_str) else 0
            except Exception as e:
                print("OpenAI error:", e)
                score = 0

        entry = ChatbotSession(
            user_id=session["user_id"], question=question, response=answer or "", score=score
        )
        db.session.add(entry)
        total_score += score
        responses_and_scores.append((question, answer, score))

    # ──────────── décision finale ────────────
    status = "RETENU" if total_score >= 30 else "REJETÉ"
    decision = Decision(
        user_id=session["user_id"],
        total_score=total_score,
        status=status,
        decision_date=db.func.now(),
    )
    db.session.add(decision)
    db.session.commit()

    # Nettoyage de session
    session.pop("questions_list", None)
    session.pop("preselected", None)

    if status == "RETENU":
        _send_invitation_email(session.get("user_email"), session["user_id"])
        flash("Félicitations ! Vous êtes retenu pour un entretien technique (email envoyé).", "success")
    else:
        flash("Merci pour votre temps. Nous vous tiendrons informé.", "info")

    session["responses_and_scores"] = responses_and_scores
    return redirect(url_for("interview.result"))

# ────────────────────────────────────────────────────────────────
#   ROUTE /interview/result
# ────────────────────────────────────────────────────────────────
@interview_bp.route("/result")
def result():
    if "user_id" not in session:
        flash("Veuillez vous connecter d'abord.", "warning")
        return redirect(url_for("auth.login"))

    decision = (
        Decision.query.filter_by(user_id=session["user_id"])
        .order_by(Decision.decision_date.desc())
        .first()
    )
    responses_and_scores = session.get("responses_and_scores", [])
    return render_template("interview/result.html", decision=decision, responses_and_scores=responses_and_scores)

# ────────────────────────────────────────────────────────────────
#   Email de convocation
# ────────────────────────────────────────────────────────────────
def _send_invitation_email(candidate_email, user_id):
    SENDER_EMAIL    = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    subject = "Convocation Entretien Technique"
    body = (
        "Bonjour,\n\n"
        "Suite à votre candidature, nous avons le plaisir de vous convoquer "
        "à un entretien technique ce lundi.\n"
        "Merci de confirmer votre présence.\n\n"
        "Cordialement,\nL'équipe RH"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = candidate_email
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("✅  Email envoyé à", candidate_email)
    except Exception as e:
        print("❌  Erreur SMTP :", e)
