import os
import json
import requests
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from pathlib import Path
from flask import render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime


env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


FIREBASE_SERVICE_ACCOUNT_JSON = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")
PROJECT_ID = os.environ.get("GCP_PROJECT") or os.environ.get("GCLOUD_PROJECT") or "shikshadrill"


import json

cred_dict = json.loads(os.environ.get("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(cred_dict)

firebase_init_kwargs = {"storageBucket": FIREBASE_STORAGE_BUCKET} if FIREBASE_STORAGE_BUCKET else {}
firebase_admin.initialize_app(cred, firebase_init_kwargs)


db = firestore.client()
bucket = storage.bucket() if FIREBASE_STORAGE_BUCKET else None 

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
active_users = {}



@app.route("/")
def splash():
    return render_template("new_logo.html")

@app.route("/signup")
def signup_page():
    return render_template("signup_with_login.html")

@app.route("/class_selection")
def class_selection():
    return render_template("class_selection.html")

@app.route("/student")
def student_page():
    return render_template("homepage_for_students.html")

@app.route("/student_profile")
def student_profile():
    return render_template("profilepage.html")

@app.route("/explore")
def explore_page():
    return render_template("explore.html")

@app.route("/science_syllabus")
def science_syllabus():
    return render_template("science_syllabus.html")

@app.route("/technology_syllabus")
def technology_syllabus():
    return render_template("technology_syllabus.html")

@app.route("/engineering_syllabus")
def engineering_syllabus():
    return render_template("engineering_syllabus.html")

@app.route("/mathematics_syllabus")
def maths_syllabus():
    return render_template("mathematics_syllabus.html")

@app.route("/science_ncert")
def science_ncert():
    return render_template("science_ncert.html")

@app.route("/technology_ncert")
def technology_ncert():
    return render_template("technology_ncert.html")

@app.route("/engineering_ncert")
def engineering_ncert():
    return render_template("engineering_ncert.html")

@app.route("/mathematics_ncert")
def maths_ncert():
    return render_template("mathematics_ncert.html")

@app.route("/science_chapvideo")
def science_chapvideo():
    return render_template("science_video.html")

@app.route("/technology_chapvideo")
def technology_chapvideo():
    return render_template("technology_video.html")

@app.route("/engineering_chapvideo")
def engineering_chapvideo():
    return render_template("engineering_video.html")

@app.route("/mathematics_chapvideo")
def mathematics_chapvideo():
    return render_template("mathematics_video.html")

@app.route("/science_testpaper")
def science_testpaper():
    return render_template("science_testpaper.html")

@app.route("/technology_testpaper")
def technology_testpaper():
    return render_template("technology_testpaper.html")

@app.route("/engineering_testpaper")
def engineering_testpaper():
    return render_template("engineering_testpaper.html")

@app.route("/mathematics_testpaper")
def mathematics_testpaper():
    return render_template("mathematics_testpaper.html")

@app.route("/roadmap")
def roadmap():
    return render_template("roadmap.html")

@app.route("/community_group")
def community_group():
    return render_template("community_group.html")

@app.route("/teacher")
def teacher_page():
    return render_template("homepage_for_teachers.html")

@app.route("/level")
def level_page():
    return render_template("level.html")

@app.route("/student_quizzes")
def student_quizzes():
    return render_template("student_quizzes.html")

@app.route("/quiz")
def quiz_page():
    return render_template("quiz.html")

@app.route("/quiz_result")
def quiz_result_page():
    return render_template("quiz_result.html")

@app.route("/science_notes")
def science_notes():
    return render_template("science_notes.html")

@app.route("/technology_notes")
def technology_notes():
    return render_template("technology_notes.html")

@app.route("/engineering_notes")
def engineering_notes():
    return render_template("engineering_notes.html")

@app.route("/mathematics_notes")
def mathematics_notes():
    return render_template("mathematics_notes.html")




@app.route("/check", methods=["GET"])
def root():
    return jsonify({"ok": True, "service": "ShikshaDrill API", "status": "running"})



def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization","")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        elif auth_header:
            token = auth_header

        if not token:
            return jsonify({"error":"Authentication required"}), 401
        
        try:
            decoded = auth.verify_id_token(token)
            request.user = decoded
        except Exception as e:
            return jsonify({"error": "Invalid token", "message": str(e)}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'student')  

    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400
    
    try:

        user = auth.create_user(email=email, password=password)
        uid = user.uid
        
        
        profile = {
            'name': name or 'Anonymous',
            'email': email,
            'role': role,  
            'xp': 0,      
            'createdAt': firestore.SERVER_TIMESTAMP  
        }
        
        
        db.collection('users').document(uid).set(profile)
        
        print(f" Created user: {uid} with role: {role}, email: {email}")  
        return jsonify({"ok": True, "uid": uid}), 201
        
    except Exception as e:
        print(f" Signup error: {e}")  
        return jsonify({"ok": False, "error": str(e)}), 400
    

@app.route('/api/login', methods = ['POST'])
def login():
    if not FIREBASE_API_KEY:
        return jsonify({"error": "FIREBASE_API_KEY not configure on server"}), 500
    
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}

    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()

        return jsonify(r.json())
    except requests.HTTPError as e:
        try:
            return jsonify(r.json()), 400
        except Exception:
            return jsonify({"error": str(e)}), 400
        

@app.route('/api/profile', methods=['GET'])
@require_auth
def get_profile():
    uid = request.user.get('uid')
    doc = db.collection('users').document(uid).get()
    if not doc.exists:
        return jsonify({"ok": False, "error": "not_found"}), 404
    
    profile = doc.to_dict()
    profile['uid'] = uid  
    
    return jsonify({"ok": True, "profile": profile})


@app.route('/api/profile', methods=['POST'])
@require_auth
def update_profile():
    uid = request.user.get('uid')
    data = request.json or {}
    db.collection('users').document(uid).set(data, merge=True)
    return jsonify({"ok": True})


@app.route('/api/upload', methods=['POST'])
@require_auth
def upload_file():
    if not bucket:
        return jsonify({"ok": False, "error": "no_storage_bucket_configured"}), 500
    if 'file' not in request.files:
        return jsonify({"ok": False, "error": "no_file"}), 400
    f = request.files['file']
    filename = f.filename
    blob = bucket.blob(f"{request.user['uid']}/{filename}")
    blob.upload_from_file(f.stream, content_type=f.content_type)
    url = blob.public_url
    return jsonify({"ok": True, "url": url})


@app.route('/api/getUserData', methods=['GET'])
def get_user_data():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    id_token = auth_header.split(" ")[1]

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        user_doc = db.collection("users").document(uid).get()
        if user_doc.exists:
            return jsonify({"ok": True, "user": user_doc.to_dict()})
        else:
            return jsonify({"error": "User data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@app.route("/create_quiz", methods=["POST"])
@require_auth
def create_quiz():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    try:
        teacher_id = request.user['uid']  
        quiz_ref = db.collection("quizzes").document()
        quiz_ref.set({
            "teacher_id": teacher_id,
            "title": data.get("title", "Untitled Quiz"),
            "class": data.get("class", ""),
            "subject": data.get("subject", "science"),
            "level": data.get("level", "easy"),
            "questions": data.get("questions", []),
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return jsonify({"success": True, "message": "Quiz saved successfully!", "quiz_id": quiz_ref.id}), 200
    except Exception as e:
        print("Error creating quiz:", e)  
        return jsonify({"success": False, "message": str(e)}), 500



@app.route("/get_quizzes", methods=["GET"])
def get_quizzes():
    try:
        teacher_id = request.args.get("teacher_id")
        level = request.args.get("level")
        subject = request.args.get("subject")
        
        print(f"=== GET QUIZZES REQUEST ===")
        print(f"Teacher ID filter: {teacher_id}")
        print(f"Level filter: {level}")
        print(f"Subject filter: {subject}")
        
        quizzes_ref = db.collection("quizzes")
        
        
        if teacher_id:
            quizzes_ref = quizzes_ref.where("teacher_id", "==", teacher_id)
        
        if level:
            quizzes_ref = quizzes_ref.where("level", "==", level)

        if subject:
            quizzes_ref = quizzes_ref.where("subject", "==", subject)

        
        quizzes = []
        for q in quizzes_ref.stream():
            quiz_data = q.to_dict()
            quiz_data['id'] = q.id
            quizzes.append(quiz_data)
        
        print(f"Found {len(quizzes)} quizzes")
        if len(quizzes) > 0:
            print("Sample quiz:", quizzes[0])
        
        return jsonify(quizzes), 200
    except Exception as e:
        print(f"Error fetching quizzes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    

@app.route("/create_puzzle_quiz", methods=["POST"])
@require_auth
def create_puzzle_quiz():
    """Create a puzzle-type quiz"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    try:
        teacher_id = request.user['uid']
        puzzle_ref = db.collection("puzzle_quizzes").document()
        
        puzzle_ref.set({
            "teacher_id": teacher_id,
            "title": data.get("title", "Untitled Puzzle"),
            "class": data.get("class", ""),
            "subject": data.get("subject", "mathematics"),
            "level": data.get("level", "easy"),
            "puzzles": data.get("puzzles", []),
            "created_at": firestore.SERVER_TIMESTAMP,
            "quiz_type": "puzzle"
        })
        
        print(f" Created puzzle quiz: {puzzle_ref.id}")
        
        return jsonify({
            "success": True, 
            "message": "Puzzle quiz created successfully!", 
            "quiz_id": puzzle_ref.id
        }), 200
        
    except Exception as e:
        print(f"Error creating puzzle quiz: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/get_puzzle_quizzes", methods=["GET"])
def get_puzzle_quizzes():
    """Get all puzzle quizzes with optional filters"""
    try:
        teacher_id = request.args.get("teacher_id")
        level = request.args.get("level")
        subject = request.args.get("subject")
        
        puzzles_ref = db.collection("puzzle_quizzes")
        
        if teacher_id:
            puzzles_ref = puzzles_ref.where("teacher_id", "==", teacher_id)
        
        if level:
            puzzles_ref = puzzles_ref.where("level", "==", level)
        
        if subject:
            puzzles_ref = puzzles_ref.where("subject", "==", subject)
        
        puzzles = []
        for p in puzzles_ref.stream():
            puzzle_data = p.to_dict()
            puzzle_data['id'] = p.id
            puzzles.append(puzzle_data)
        
        print(f" Found {len(puzzles)} puzzle quizzes")
        
        return jsonify(puzzles), 200
        
    except Exception as e:
        print(f"Error fetching puzzle quizzes: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/get_puzzle_quiz", methods=["GET"])
def get_puzzle_quiz():
    """Get a single puzzle quiz by ID"""
    quiz_id = request.args.get("id")
    
    if not quiz_id:
        return jsonify({"error": "Quiz ID required"}), 400
    
    try:
        doc = db.collection("puzzle_quizzes").document(quiz_id).get()
        if doc.exists:
            puzzle_data = doc.to_dict()
            puzzle_data['id'] = doc.id
            return jsonify(puzzle_data), 200
        else:
            return jsonify({"error": "Puzzle quiz not found"}), 404
    except Exception as e:
        print(f"Error fetching puzzle quiz: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/delete_puzzle_quiz", methods=["DELETE"])
@require_auth
def delete_puzzle_quiz():
    """Delete a puzzle quiz"""
    quiz_id = request.args.get("id")
    
    if not quiz_id:
        return jsonify({"success": False, "message": "Quiz ID required"}), 400
    
    try:
        quiz_ref = db.collection("puzzle_quizzes").document(quiz_id)
        quiz = quiz_ref.get()
        
        if not quiz.exists:
            return jsonify({"success": False, "message": "Quiz not found"}), 404
        
        quiz_data = quiz.to_dict()
        teacher_id = request.user.get('uid')
        
        if quiz_data.get('teacher_id') != teacher_id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        quiz_ref.delete()
        
        return jsonify({"success": True, "message": "Puzzle quiz deleted successfully"}), 200
        
    except Exception as e:
        print(f" Error deleting puzzle quiz: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/puzzle_quiz")
def puzzle_quiz_page():
    """Route to puzzle quiz page"""
    return render_template("puzzle_quiz.html")
    

@app.route("/update_quiz", methods=["POST"])
@require_auth
def update_quiz():
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    quiz_id = data.get("quiz_id")
    
    if not quiz_id:
        return jsonify({"success": False, "message": "Quiz ID required"}), 400
    
    try:
        quiz_ref = db.collection("quizzes").document(quiz_id)
        quiz = quiz_ref.get()
        
        if not quiz.exists:
            return jsonify({"success": False, "message": "Quiz not found"}), 404
        
        
        quiz_data = quiz.to_dict()
        teacher_id = request.user.get('uid')
        
        if quiz_data.get('teacher_id') != teacher_id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        
        quiz_ref.update({
            "title": data.get("title", "Untitled Quiz"),
            "class": data.get("class", ""),
            "subject": data.get("subject", "science"),
            "level": data.get("level", "easy"),  
            "questions": data.get("questions", []),
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"success": True, "message": "Quiz updated successfully!", "quiz_id": quiz_id}), 200
    except Exception as e:
        print(f"Error updating quiz: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    


@app.route("/submit_quiz_attempt", methods=["POST"])
@require_auth
def submit_quiz_attempt():
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    try:
        student_id = request.user.get('uid')
        quiz_id = data.get("quiz_id")
        score = data.get("score", 0)
        total_questions = data.get("total_questions", 0)
        
        
        attempt_ref = db.collection("quiz_attempts").document()
        attempt_ref.set({
            "student_id": student_id,
            "quiz_id": quiz_id,
            "score": score,
            "total_questions": total_questions,
            "percentage": round((score / total_questions * 100) if total_questions > 0 else 0, 2),
            "attempted_at": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"success": True, "message": "Quiz attempt recorded"}), 200
    except Exception as e:
        print(f"Error recording attempt: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    

@app.route("/get_quiz_attempts", methods=["GET"])
@require_auth
def get_quiz_attempts():
    try:
        teacher_id = request.args.get("teacher_id")
        
        if not teacher_id:
            return jsonify({"error": "Teacher ID required"}), 400
        
       
        quizzes_ref = db.collection("quizzes").where("teacher_id", "==", teacher_id).stream()
        quiz_ids = [q.id for q in quizzes_ref]
        
        if not quiz_ids:
            return jsonify({
                "totalAttempts": 0,
                "avgScore": 0,
                "quizPerformance": []
            }), 200
        
        
        attempts = []
        for quiz_id in quiz_ids:
            attempts_ref = db.collection("quiz_attempts").where("quiz_id", "==", quiz_id).stream()
            for attempt in attempts_ref:
                attempt_data = attempt.to_dict()
                attempt_data['quiz_id'] = quiz_id
                attempts.append(attempt_data)
        
        
        total_attempts = len(attempts)
        avg_score = round(sum(a.get('percentage', 0) for a in attempts) / total_attempts, 2) if total_attempts > 0 else 0
        
       
        quiz_performance = {}
        for attempt in attempts:
            qid = attempt['quiz_id']
            if qid not in quiz_performance:
                quiz_performance[qid] = {'scores': [], 'quizTitle': ''}
            quiz_performance[qid]['scores'].append(attempt.get('percentage', 0))
        
        
        performance_list = []
        for qid, data in quiz_performance.items():
            quiz_doc = db.collection("quizzes").document(qid).get()
            if quiz_doc.exists:
                quiz_title = quiz_doc.to_dict().get('title', 'Untitled')
                avg = round(sum(data['scores']) / len(data['scores']), 2) if data['scores'] else 0
                performance_list.append({
                    'quizTitle': quiz_title,
                    'avgScore': avg,
                    'attempts': len(data['scores'])
                })
        
        return jsonify({
            "totalAttempts": total_attempts,
            "avgScore": avg_score,
            "quizPerformance": performance_list
        }), 200
        
    except Exception as e:
        print(f"Error fetching attempts: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/delete_quiz", methods=["DELETE"])
@require_auth
def delete_quiz():
    quiz_id = request.args.get("id")
    
    if not quiz_id:
        return jsonify({"success": False, "message": "Quiz ID required"}), 400
    
    try:
        
        quiz_ref = db.collection("quizzes").document(quiz_id)
        quiz = quiz_ref.get()
        
        if not quiz.exists:
            return jsonify({"success": False, "message": "Quiz not found"}), 404
        
        
        quiz_data = quiz.to_dict()
        teacher_id = request.user.get('uid')
        
        if quiz_data.get('teacher_id') != teacher_id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
       
        quiz_ref.delete()
        
        return jsonify({"success": True, "message": "Quiz deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting quiz: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    


@app.route("/get_quiz", methods=["GET"])
def get_quiz():
    quiz_id = request.args.get("id")
    
    if not quiz_id:
        return jsonify({"error": "Quiz ID required"}), 400
    
    try:
        doc = db.collection("quizzes").document(quiz_id).get()
        if doc.exists:
            quiz_data = doc.to_dict()
            quiz_data['id'] = doc.id
            return jsonify(quiz_data), 200
        else:
            return jsonify({"error": "Quiz not found"}), 404
    except Exception as e:
        print(f"Error fetching quiz: {e}")
        return jsonify({"error": str(e)}), 500
    

@app.route("/update_student_xp", methods=["POST"])
@require_auth
def update_student_xp():
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    try:
        student_id = request.user.get('uid')
        xp_earned = data.get("xp", 0)
        
        
        student_ref = db.collection('users').document(student_id)
        student_doc = student_ref.get()
        
        if not student_doc.exists:
            return jsonify({"success": False, "message": "Student not found"}), 404
        
        student_data = student_doc.to_dict()
        current_xp = student_data.get('xp', 0)
        new_xp = current_xp + xp_earned
        
        
        student_ref.update({
            "xp": new_xp,
            "last_xp_update": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            "success": True, 
            "message": "XP updated successfully",
            "new_xp": new_xp
        }), 200
        
    except Exception as e:
        print(f"Error updating XP: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/get_student_xp", methods=["GET"])
@require_auth
def get_student_xp():
    try:
        student_id = request.user.get('uid')
        
        student_doc = db.collection('users').document(student_id).get()
        
        if not student_doc.exists:
            return jsonify({"xp": 0}), 200
        
        student_data = student_doc.to_dict()
        xp = student_data.get('xp', 0)
        
        return jsonify({"xp": xp}), 200
        
    except Exception as e:
        print(f"Error fetching XP: {e}")
        return jsonify({"xp": 0}), 200
    

@app.route("/get_all_students", methods=["GET"])
@require_auth
def get_all_students():
    """Get all students - only accessible by teachers"""
    try:
        
        uid = request.user.get('uid')
        print(f" Teacher UID requesting students: {uid}")
        
        teacher_doc = db.collection('users').document(uid).get()
        
        if not teacher_doc.exists:
            print(f" Teacher document not found for UID: {uid}")
            return jsonify({"error": "User not found"}), 404
        
        teacher_data = teacher_doc.to_dict()
        print(f" Teacher data: name={teacher_data.get('name')}, role={teacher_data.get('role')}")
        
        if teacher_data.get('role') != 'teacher':
            print(f" User is not a teacher. Role: {teacher_data.get('role')}")
            return jsonify({"error": "Unauthorized - Teachers only"}), 403
        
        
        print("=" * 50)
        print(" CHECKING ALL USERS IN DATABASE:")
        all_users_ref = db.collection('users').stream()
        all_count = 0
        student_count = 0
        
        for u in all_users_ref:
            all_count += 1
            u_data = u.to_dict()
            role = u_data.get('role', 'NO_ROLE')
            print(f"  - User {u.id[:8]}...: role={role}, email={u_data.get('email')}, name={u_data.get('name')}")
            if role == 'student':
                student_count += 1
        
        print(f" Total users: {all_count}, Students with role='student': {student_count}")
        print("=" * 50)
        
        
        students_ref = db.collection('users').where('role', '==', 'student').stream()
        
        students = []
        for student in students_ref:
            student_data = student.to_dict()
            student_data['id'] = student.id
            
            student_data.pop('password', None)
            students.append(student_data)
        
        print(f" Returning {len(students)} students to frontend")
        
        return jsonify({"success": True, "students": students}), 200
        
    except Exception as e:
        print(f" Error fetching students: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    

@app.route("/fix_existing_students", methods=["POST"])
@require_auth
def fix_existing_students():
    """One-time fix: Ensure all users have proper role and xp fields"""
    try:
        
        uid = request.user.get('uid')
        teacher_doc = db.collection('users').document(uid).get()
        
        if not teacher_doc.exists:
            return jsonify({"error": "User not found"}), 404
        
        teacher_data = teacher_doc.to_dict()
        if teacher_data.get('role') != 'teacher':
            return jsonify({"error": "Unauthorized - Teachers only"}), 403
        
        
        users_ref = db.collection('users').stream()
        
        fixed_count = 0
        fixed_users = []
        
        for user_doc in users_ref:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            
            updates = {}
            
            
            if 'role' not in user_data or not user_data.get('role'):
                
                if user_id == uid:
                    updates['role'] = 'teacher'
                else:
                    updates['role'] = 'student'
            
            
            if user_data.get('role') == 'student' or updates.get('role') == 'student':
                if 'xp' not in user_data:
                    updates['xp'] = 0
            
            
            if updates:
                db.collection('users').document(user_id).update(updates)
                fixed_count += 1
                fixed_users.append({
                    'id': user_id[:8] + '...',
                    'email': user_data.get('email'),
                    'updates': updates
                })
                print(f" Fixed user {user_id}: {updates}")
        
        return jsonify({
            "success": True, 
            "message": f"Fixed {fixed_count} users",
            "fixed_count": fixed_count,
            "fixed_users": fixed_users
        }), 200
        
    except Exception as e:
        print(f" Error fixing users: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/assign_roll_number", methods=["POST"])
@require_auth
def assign_roll_number():
    """Assign or update roll number for a student"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    try:
        
        uid = request.user.get('uid')
        teacher_doc = db.collection('users').document(uid).get()
        
        if not teacher_doc.exists:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        teacher_data = teacher_doc.to_dict()
        if teacher_data.get('role') != 'teacher':
            return jsonify({"success": False, "message": "Unauthorized - Teachers only"}), 403
        
        student_id = data.get("student_id")
        roll_number = data.get("roll_number")
        
        if not student_id or not roll_number:
            return jsonify({"success": False, "message": "Student ID and roll number required"}), 400
        
        
        student_ref = db.collection('users').document(student_id)
        student_doc = student_ref.get()
        
        if not student_doc.exists:
            return jsonify({"success": False, "message": "Student not found"}), 404
        
        
        student_ref.update({
            "roll_number": roll_number,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            "success": True, 
            "message": "Roll number assigned successfully"
        }), 200
        
    except Exception as e:
        print(f"Error assigning roll number: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/delete_student", methods=["DELETE"])
@require_auth
def delete_student():
    """Delete a student - only accessible by teachers"""
    try:
        
        uid = request.user.get('uid')
        teacher_doc = db.collection('users').document(uid).get()
        
        if not teacher_doc.exists:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        teacher_data = teacher_doc.to_dict()
        if teacher_data.get('role') != 'teacher':
            return jsonify({"success": False, "message": "Unauthorized - Teachers only"}), 403
        
        student_id = request.args.get("id")
        
        if not student_id:
            return jsonify({"success": False, "message": "Student ID required"}), 400
        
        
        db.collection('users').document(student_id).delete()
        
        
        try:
            auth.delete_user(student_id)
        except Exception as e:
            print(f"Error deleting from Firebase Auth: {e}")
        
        return jsonify({"success": True, "message": "Student deleted successfully"}), 200
        
    except Exception as e:
        print(f"Error deleting student: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_users:
        username = active_users[request.sid]
        del active_users[request.sid]
        emit('user_left', {'username': username}, broadcast=True)
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_chat')
def handle_join(data):
    """User joins the chat with authentication"""
    token = data.get('token')
    
    if not token:
        emit('error', {'message': 'Authentication required'})
        return
    
    try:
        decoded = auth.verify_id_token(token)
        uid = decoded['uid']
        
        user_doc = db.collection('users').document(uid).get()
        if not user_doc.exists:
            emit('error', {'message': 'User not found'})
            return
        
        user_data = user_doc.to_dict()
        username = user_data.get('name', 'Anonymous')
        
        active_users[request.sid] = {
            'uid': uid,
            'username': username,
            'avatar': user_data.get('currentAvatar', '/static/models/female_avatar.glb'),
            'gender': user_data.get('profileGender', 'female')
        }
        
        join_room('main_chat')
        
        emit('user_joined', {
            'username': username,
            'message': f'{username} joined the chat!'
        }, room='main_chat', include_self=False)
        
        emit('active_users', {
            'users': list(active_users.values())
        })
        
        print(f'✅ {username} joined the chat')
        
    except Exception as e:
        print(f'❌ Error in join_chat: {e}')
        emit('error', {'message': 'Authentication failed'})

@socketio.on('send_message')
def handle_message(data):
    """Handle new message from user"""
    if request.sid not in active_users:
        emit('error', {'message': 'Not authenticated'})
        return
    
    user_info = active_users[request.sid]
    
    message_data = {
        'id': f'msg_{datetime.now().timestamp()}',
        'uid': user_info['uid'],
        'author': user_info['username'],
        'text': data.get('text', ''),
        'image': data.get('image', None),
        'avatar': user_info['avatar'],
        'timestamp': datetime.now().isoformat(),
        'replyTo': data.get('replyTo', None)
    }
    
    try:
        db.collection('chat_messages').add(message_data)
    except Exception as e:
        print(f'Error saving message: {e}')
    
    emit('new_message', message_data, room='main_chat', include_self=True)
    
    print(f'📨 Message from {user_info["username"]}: {data.get("text", "")[:50]}')

@socketio.on('add_reaction')
def handle_reaction(data):
    """Handle reaction to a message"""
    if request.sid not in active_users:
        return
    
    user_info = active_users[request.sid]
    
    reaction_data = {
        'messageId': data.get('messageId'),
        'emoji': data.get('emoji'),
        'username': user_info['username']
    }
    
    emit('reaction_added', reaction_data, room='main_chat', include_self=True)

@socketio.on('add_comment')
def handle_comment(data):
    """Handle comment on a message"""
    if request.sid not in active_users:
        return
    
    user_info = active_users[request.sid]
    
    comment_data = {
        'messageId': data.get('messageId'),
        'author': user_info['username'],
        'text': data.get('text'),
        'timestamp': datetime.now().isoformat()
    }
    
    emit('comment_added', comment_data, room='main_chat', include_self=True)

@socketio.on('get_chat_history')
def handle_get_history(data):
    """Get chat history from Firestore"""
    try:
        messages_ref = db.collection('chat_messages').order_by('timestamp', direction='DESCENDING').limit(50)
        messages = []
        
        for msg in messages_ref.stream():
            msg_data = msg.to_dict()
            msg_data['id'] = msg.id
            messages.append(msg_data)
        
        messages.reverse()
        
        emit('chat_history', {'messages': messages})
        
    except Exception as e:
        print(f'Error fetching chat history: {e}')
        emit('error', {'message': 'Failed to load chat history'})



@app.route('/_ah/health')
def health():
    return ('ok', 200)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
