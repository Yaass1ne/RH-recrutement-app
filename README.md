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
- Admin interface for easy job and candidate management.

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

**Step 4: Set Environment Variables**

**Windows**:
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
set SENDER_EMAIL=your_email@example.com
set SENDER_PASSWORD=your_email_password
```

**Linux/MacOS**:
```bash
export OPENAI_API_KEY=your_openai_api_key_here
export SENDER_EMAIL=your_email@example.com
export SENDER_PASSWORD=your_email_password
```

Replace the placeholders (`your_openai_api_key_here`, `your_email@example.com`, and `your_email_password`) with your actual details.

To generate an app-specific password , you need to enable 2-Step Verification on your Gmail account. Then go to your Google Account > Security > App passwords, select “Mail” and your device, and Google will generate a unique 16-character password for use in applications like this one. 
This is different from your regular Gmail login password and is required for secure SMTP access.

**Step 5: Launch Application**

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

