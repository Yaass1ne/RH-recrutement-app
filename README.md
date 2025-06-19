# Automated Candidate Filtering System

This Flask-based project automates candidate filtering through two main processes:

1. **Semantic CV Filtering**
   - Uses NLP techniques (**spaCy**, **SBERT**) to match candidate resumes semantically to the provided job descriptions.

2. **Chatbot Interview & Scoring**
   - Utilizes **GPT-3.5** to generate custom interview questions based on job descriptions.
   - Automatically scores candidate responses using AI to determine their suitability.

---

## Features Overview

- Extract text from uploaded CV PDFs automatically.
- Semantic CV-to-job matching and scoring using advanced NLP.
- AI-generated interview questions and scoring through GPT-3.5.
- Automatic email notifications for candidate interviews.
- Admin interface for easy job and candidate management and logs.

---

## Getting Started

### Prerequisites

- **XAMPP** (with MySQL database)
- **Python 3.8**

### Installation Guide

**Step 1: Database Setup**

- Run XAMPP and start MySQL service.
- Create a database named `nlp_rec`.

**Step 2: Python Virtual Environment**

```bash
python3.8 -m venv venv
```

Activate the environment:

- **Windows**:
```bash
venv\Scripts\activate
```

- **Linux/MacOS**:
```bash
source venv/bin/activate
```

**Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_md
```

**Step 4: Launch Application**

```bash
flask run
```

---

## Project File Structure

```
project-root/
├── admin.py
├── app.py
├── auth.py
├── config.py
├── cv.py
├── extensions.py
├── interview.py
├── jobs.py
├── models.py
├── requirements.txt
├── static/
├── templates/
├── uploads/
└── README.md
```

---

## Contributors

- Yassine Yahyaoui

---

## Future Enhancements

- Docker-based deployment.
- Advanced analytics dashboard.
- Fully open-source NLP integration.

