# Automated Answer Script Evaluation System Using AI

> **A full-stack web application built for college hackathons to automatically evaluate descriptive student answer scripts using Natural Language Processing (NLP) and Artificial Intelligence.**

---

## 🌟 Project Overview

Evaluating descriptive examination answer scripts manually is time-consuming, subjective, and prone to grading inconsistencies. The **Automated Answer Script Evaluation System** solves this challenge by leveraging NLP algorithms (TF-IDF vectorization, Cosine Similarity, Synonym Matching, and Structural Grammar Analysis) to evaluate student responses against reference model answers automatically.

The system awards fair partial marks, extracts matched and missing key concepts, calculates an **AI Confidence Score**, produces printable PDF grade sheets, exports Excel marksheets, and provides interactive role-based dashboards for Admins, Teachers, and Students.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3 (Glassmorphism & Variables), Modern Vanilla JavaScript, Chart.js, FontAwesome.
- **Backend**: Python 3.12, Flask 3.x, Flask-Login, Flask-SQLAlchemy, Werkzeug Security.
- **Database**: MySQL 8.0+ / SQLite (automatic zero-friction fallback).
- **AI / NLP**: `scikit-learn` (TF-IDF Vectorizer & Cosine Similarity), `nltk` (WordNet Synonyms, Tokenizer, Stopwords, PorterStemmer).
- **Report Generation**: `reportlab` (PDF Grade Sheets), `pandas` & `openpyxl` (Excel Marksheets).

---

## 🔬 AI Evaluation Workflow & Algorithm

```
[Student Answer Script]  +  [Model Reference Answer]
         │                          │
         ▼                          ▼
 ┌──────────────────────────────────────────────┐
 │             Preprocessing & NLP              │
 │  • Tokenization & Lowercasing                │
 │  • NLTK Stopword Filtering                   │
 │  • Porter Stemming & WordNet Lemmatization   │
 └──────────────────────┬───────────────────────┘
                        │
                        ▼
 ┌──────────────────────────────────────────────┐
 │              Evaluation Pipeline             │
 │  1. Semantic Similarity (TF-IDF + Cosine)   │
 │  2. Keyword & Technical Term Synonym Match   │
 │  3. Structural Grammar & Quality Check      │
 └──────────────────────┬───────────────────────┘
                        │
                        ▼
 ┌──────────────────────────────────────────────┐
 │         Partial Marks Calculation            │
 │  Score = (Sim * 0.50) + (KW * 0.35) +       │
 │          (Grammar * 0.15)                    │
 └──────────────────────┬───────────────────────┘
                        │
                        ▼
 [Final Marks | AI Feedback | PDF Report | Excel Export]
```

$$\text{Final Marks} = \text{Max Marks} \times (0.50 \times \text{Similarity Score} + 0.35 \times \text{Keyword Score} + 0.15 \times \text{Grammar Score})$$

---

## 🗄️ Database Schema

The system uses 6 normalized tables with foreign keys and cascade delete rules:
- `users`: `id`, `name`, `email`, `password_hash`, `role` (`admin`, `teacher`, `student`), `profile_pic`, `created_at`
- `subjects`: `subject_id`, `subject_name`, `subject_code`, `teacher_id`
- `exams`: `exam_id`, `subject_id`, `exam_name`, `exam_date`, `total_marks`
- `questions`: `question_id`, `exam_id`, `question_text`, `model_answer`, `keywords`, `max_marks`
- `student_answers`: `answer_id`, `student_id`, `question_id`, `answer_text`, `uploaded_file`, `submitted_at`
- `evaluations`: `evaluation_id`, `answer_id`, `student_id`, `question_id`, `similarity_score`, `grammar_score`, `keyword_score`, `confidence_score`, `obtained_marks`, `feedback`, `matched_keywords`, `missing_keywords`, `evaluated_date`

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

Open browser at: `http://127.0.0.1:5000`

---

## 🔑 Pre-Loaded Hackathon Demo Credentials

| Role | Email | Password | Features |
|---|---|---|---|
| **Admin** | `admin@eval.ai` | `admin123` | System metrics, pass %, user directory, delete users |
| **Teacher** | `turing@university.edu` | `teacher123` | Create exams, set model answers, batch AI evaluation, Excel export |
| **Student** | `john@student.edu` | `student123` | Submit answers, inspect AI breakdown, download PDF grade sheet |

---

## 📤 Manual GitHub Repository Push Instructions

To push this project to your custom GitHub repository:

```bash
# 1. Add your remote repository URL
git remote add origin https://github.com/<your-username>/Automated-Answer-Script-Evaluation.git

# 2. Rename branch to main
git branch -M main

# 3. Push code to GitHub
git push -u origin main
```

---

## 👥 Contributors & License

Developed for College Hackathon 2026. Distributed under the MIT License.
