# 🎓 ShikshaDrill

**Interactive STEM Learning Platform with Live Chat, Quizzes, and Gamification**

---

## 🚀 Overview

ShikshaDrill is an interactive learning platform designed to make education engaging, collaborative, and practical. It combines real-time communication, structured study content, and gamified quizzes to enhance student learning experiences.

---

## 🌐 Live Demo

🚀 **Backend Live URL:**  
https://shikshadrill.onrender.com

---

## ✨ Features

* 📚 **Subject-wise Learning Content** (NCERT, syllabus, videos, test papers)
* 🧠 **Interactive Quizzes & Puzzle Games**
* 💬 **Live Chat System (Real-time communication using SocketIO)**
* 👩‍🏫 **Student & Teacher Dashboards**
* 🎯 **Gamified Learning Experience**
* 🔥 **Firebase Integration (Authentication, Firestore, Storage)**

---

## 🛠️ Tech Stack

**Frontend:**

* HTML, CSS, JavaScript

**Backend:**

* Python (Flask)
* Flask-SocketIO

**Database & Services:**

* Firebase (Auth, Firestore, Storage)

**Other Tools:**

* Docker
* REST APIs

**Deployment:**

- Backend hosted on **Render**
- Uses **Gunicorn** for production server
- Environment variables managed securely via Render dashboard
  
---

## 📁 Project Structure

```
ShikshaDrill_Project/
│
├── backend/
│   ├── app.py
│   ├── templates/
│   ├── static/
│
├── .env (ignored)
├── serviceAccountKey.json (ignored)
├── requirements.txt
├── Dockerfile
└── firebase.json
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/Sakshichaubey14/SHIKSHADRILL_PROJECT.git
cd SHIKSHADRILL_PROJECT
```

### 2. Create virtual environment

```
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Add environment variables

Create `.env` file and add:

```
FIREBASE_API_KEY=your_key
FIREBASE_STORAGE_BUCKET=your_bucket
GCP_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=backend/serviceAccountKey.json
```

---

### 5. Run the application

```
python backend/app.py
```

---

## 🔐 Security Note

Sensitive files like `.env` and `serviceAccountKey.json` are not included in the repository for security reasons.

---

## 🎯 Future Improvements

* AI-based personalized learning
* Performance analytics dashboard
* Mobile app integration
* Leaderboard & achievements system

---

## 👥 Team (Smart India Hackathon)

**Team Leader**  
- Sakshi Chaubey – Led backend development, Firebase integration, and deployment on Render

**Team Members**  
1. Khateeba Ruhulla  
2. Suhani Maurya  
3. Jahnvi Agrahari  
4. Mohd Huzaifa Khan  
5. Akshay Yadav

**👨‍🏫 Mentor**

- Mr. Atif Bashir – Guided the project development and provided technical insights.
  
---

## 💡 Inspiration

Built as part of **Smart India Hackathon (SIH)** to create an engaging and accessible digital learning platform.

---
