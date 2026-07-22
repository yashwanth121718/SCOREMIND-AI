# ScoreMind AI – Intelligent Educational Assessment Platform

> **ScoreMind AI** is an intelligent, AI-powered educational assessment platform that automates descriptive answer script evaluation, provides fair and transparent scoring, detects plagiarism, delivers personalized feedback, and helps students improve through actionable learning insights. It aims to reduce teachers' workload while improving the quality, consistency, and speed of academic assessment.

---

## 🌟 Vision Statement

> *"ScoreMind AI automates descriptive answer script evaluation, provides fair and transparent scoring, detects plagiarism, delivers personalized feedback, and helps students improve through actionable learning insights, reducing teachers' workload while improving academic quality and speed."*

---

## 🚀 Unique Hackathon Features

1. **📝 OCR & Handwriting Recognition** ([advanced_features.py](file:///c:/Users/YASHWANTH%20J/Documents/HACKATHON/advanced_features.py)): Scans uploaded handwritten answer sheets (`.png`, `.jpg`, `.pdf`) via Tesseract OCR and evaluates extracted text automatically.
2. **🛡️ Plagiarism Detection Engine**: Cross-compares student submissions to flag copied sentences and calculate similarity ratios between peers.
3. **⚡ AI Model Answer & Rubric Generator**: Auto-generates model answers, keywords, mark rubrics, and Bloom's Taxonomy levels based on question prompts.
4. **📈 Performance Predictor & Student Leaderboard**: Predicts semester marks, pass probability, class rank, and generates personalized revision roadmaps.
5. **📲 QR Verified PDF Certificates**: Generates printable PDF grade sheets and downloadable Certificates of Excellence verified via QR Codes (`/verify/<eval_id>`).
6. **🤖 Floating AI Mentor Chatbot**: Instant AI assistant on every page to answer student and teacher questions.
7. **🎮 Gamification System**: XP Points, Daily Streaks, Level Progression, and Achievement Badges.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3 (Glassmorphism & Variables), Modern Vanilla JavaScript, Chart.js, FontAwesome.
- **Backend**: Python 3.12, Flask 3.x, Flask-Login, Flask-SQLAlchemy, Werkzeug Security.
- **Database**: MySQL 8.0+ / SQLite (automatic zero-friction fallback).
- **AI / NLP**: `scikit-learn` (TF-IDF Vectorizer & Cosine Similarity), `nltk` (WordNet Synonyms, Tokenizer, Stopwords, PorterStemmer), `pytesseract` (OCR).
- **Report & Certificate Generation**: `reportlab` (PDF Grade Sheets & Certificates), `pandas` & `openpyxl` (Excel Marksheets).

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
| **Student** | `john@student.edu` | `student123` | Submit answers, inspect AI breakdown, gamification XP, PDF certificate |

---

## 📤 Manual GitHub Repository Push Instructions

```bash
# 1. Add your remote repository URL
git remote add origin https://github.com/<your-username>/ScoreMind-AI.git

# 2. Rename branch to main
git branch -M main

# 3. Push code to GitHub
git push -u origin main
```
