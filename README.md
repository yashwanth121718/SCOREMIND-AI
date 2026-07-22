# Automated Answer Script Evaluation System Using AI

> **A full-stack web application built for college hackathons to automatically evaluate descriptive student answer scripts using Natural Language Processing (NLP) and Artificial Intelligence.**

---

##  Key Features

- ** Role-Based Access Control**:
  - **Admin**: Dashboard metrics, system user directory, subject/exam overview, user management.
  - **Teacher**: Subject & Exam creator, question bank with model answers and keyword weightings, student answer script reviews, single & batch AI evaluations, and Excel gradebook export.
  - **Student**: View assigned exams, submit descriptive answers via text or file script uploads, inspect instant AI mark breakdowns, and download PDF grade sheets.

- ** Advanced AI/NLP Evaluation Engine**:
  - **Preprocessing**: Sentence tokenization, NLTK stopword removal, stemming (PorterStemmer) & lemmatization.
  - **Semantic Similarity**: Vector space TF-IDF Vectorizer + Cosine Similarity calculation.
  - **Keyword Matching Engine**: Technical concept extraction identifying present vs missing key terms.
  - **Grammar & Quality Score**: Sentence structure, length adequacy ratio, and capitalization checks.
  - **Partial Marking System**:
    $$\text{Final Marks} = \text{Max Marks} \times (0.50 \times \text{Similarity} + 0.35 \times \text{Keyword Score} + 0.15 \times \text{Grammar Score})$$
  - **Actionable AI Feedback**: Automatically generated diagnostic comments explaining mark breakdown.

- ** Reports & Analytics**:
  - Printable **PDF Grade Sheet Report** per student evaluation (powered by ReportLab).
  - Comprehensive **Excel/CSV Marksheets** for entire exams (powered by Pandas / OpenPyXL).
  - Interactive **Chart.js** performance graphs.

- ** Zero-Friction Database Setup**:
  - Automatic **MySQL** connection engine with **SQLite** fallback out of the box.
  - Pre-populated with realistic hackathon demo data (Admin, Teachers, Students, Subjects, Exams, Questions, Answers, Evaluations).

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3 (Glassmorphism & Variables), Modern Vanilla JavaScript, Chart.js, FontAwesome.
- **Backend**: Python 3.12, Flask 3.x, Flask-Login, Flask-SQLAlchemy, Werkzeug Security.
- **Database**: MySQL / SQLite (fallback).
- **AI / NLP**: `scikit-learn`, `nltk`, `sentence-transformers` (optional).
- **Report Generation**: `reportlab` (PDF), `pandas` & `openpyxl` (Excel).

---

## 🚀 Quick Setup & Hackathon Execution Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Pre-Loaded Demo Credentials

| Role | Email | Password | Dashboard Features |
|---|---|---|---|
| **Admin** | `admin@eval.ai` | `admin123` | User directory, stats, user deletion |
| **Teacher** | `turing@university.edu` | `teacher123` | Create exams, add model answers, run AI eval |
| **Student** | `john@student.edu` | `student123` | Submit answers, view AI feedback, download PDF |

---

## 📁 Project Structure

```
Automated-Answer-Script-Evaluation/
├── app.py                     # Flask application factory
├── config.py                  # App configuration & DB settings
├── database.py                # MySQL / SQLite fallback connection & seeder
├── models.py                  # SQLAlchemy database models
├── routes.py                  # Auth, Admin, Teacher, Student endpoints
├── ai_module.py               # Core AI/NLP evaluation algorithms
├── evaluation.py              # Evaluation workflow manager
├── reports.py                 # PDF & Excel report generators
├── requirements.txt           # Python dependencies
├── README.md                  # Detailed project documentation
├── .gitignore                 # Git ignore rules
├── sql/
│   └── database.sql           # MySQL database schema & sample data
├── static/
│   ├── css/
│   │   ├── style.css          # Main Glassmorphism UI theme
│   │   └── dashboard.css      # Metric cards, tables, charts styling
│   ├── js/
│   │   ├── script.js          # Theme toggler & toast alerts
│   │   ├── validation.js      # Client-side form & file validation
│   │   └── dashboard.js       # Live search & Chart.js setup
│   └── uploads/               # Answer files & user avatars
├── reports/                   # Generated PDF & Excel files
└── templates/                 # HTML5 Jinja2 Templates
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── admin_dashboard.html
    ├── teacher_dashboard.html
    ├── student_dashboard.html
    ├── upload_answers.html
    ├── evaluation.html
    └── profile.html
```
