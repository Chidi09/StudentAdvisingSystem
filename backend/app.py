# StudentAdvisingSystem/backend/app.py
import os
import traceback
import random
import string
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from dotenv import load_dotenv

from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt
)
from flask_mail import Message

# Import extensions
from extensions import db, migrate, jwt, mail, cors # Keep these imports as they are used for init_app later

# --- Import ALL Models used in this file ---
from models.degree import Degree
from models.course import Course
from models.student import Student
from models.lecturer import Lecturer
from models.advising_resource import AdvisingResource
from models.note import AdvisingNote
from models.enrollment import Enrollment
from models.result import Result
# --- End Model Imports ---

# Import CORS directly for explicit configuration
from flask_cors import CORS # ADDED THIS LINE

load_dotenv()
# --- ADDED THIS LINE AS REQUESTED ---
print("✅ DATABASE_URL =", os.getenv("DATABASE_URL"))
# --- END ADDED LINE ---
app = Flask(__name__)

ENVIRONMENT = os.getenv('FLASK_ENV', 'development')


# --- App Configurations ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-super-secret-key-change-in-env')
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 1)))

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.example.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your-email@example.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your-email-password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', ('Crawford Advising Portal', 'noreply@crawforduniversity.edu.ng'))

db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
mail.init_app(app)

# REFINED CORS INITIALIZATION:
# This ensures CORS headers are applied directly to the app for /api/* routes.
# It explicitly allows requests from your frontend's origin (http://127.0.0.1:5500)
# and enables support for credentials (like JWT tokens).
CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500", "supports_credentials": True}})

# The existing cors.init_app from extensions.py is still present,
# but the direct CORS(app, ...) call above is more robust for /api/* routes.
# The allowed_origins in the development block below is also corrected to 5500.
if ENVIRONMENT == 'development':
    allowed_origins = ["http://localhost:5500", "http://127.0.0.1:5500", "null"] # Corrected to 5500
    # The cors.init_app from extensions is still called, but the direct CORS(app, ...)
    # above will take precedence for the /api/* routes concerning the origin.
    cors.init_app(app, origins=allowed_origins, methods=["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"], allow_headers=["Content-Type", "Authorization", "X-Requested-With"], supports_credentials=True, expose_headers=["Content-Type", "Authorization"])
    app.logger.info(f"CORS configured for development with origins: {allowed_origins} for all routes via extensions.")
else:
    allowed_origins = [os.getenv("FRONTEND_URL", "https://your-production-domain.com")]
    cors.init_app(app, origins=allowed_origins, methods=["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"], allow_headers=["Content-Type", "Authorization", "X-Requested-With"], supports_credentials=True, expose_headers=["Content-Type", "Authorization"])
    app.logger.info(f"CORS configured for production with origins: {allowed_origins} for all routes via extensions.")


def generate_random_numeric_password(length=8):
    return ''.join(random.choices(string.digits, k=length))

def get_typed_user_from_jwt_v2():
    try:
        user_id_str = get_jwt_identity()
        claims = get_jwt()
        user_type = claims.get("user_type")
        if not user_id_str or not user_type:
            app.logger.warning("Token missing identity or user_type claim.")
            return None, None
        user_id = int(user_id_str)
        if user_type == "student": return db.session.get(Student, user_id), user_type
        elif user_type == "lecturer": return db.session.get(Lecturer, user_id), user_type
        else: app.logger.warning(f"Unknown user type in token: {user_type}"); return None, None
    except Exception as e:
        app.logger.error(f"Error getting user from JWT: {str(e)}", exc_info=True); return None, None

@app.route('/')
def index(): return jsonify({"message": "Welcome to Student Advising System API"})

# --- Authentication APIs ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data: return jsonify({"success": False, "message": "Request body must be JSON."}), 400
    username_or_email = data.get('username')
    password = data.get('password')
    if not username_or_email or not password: return jsonify({"success": False, "message": "Username/Email and password are required."}), 400

    try: # ADDED TRY-EXCEPT BLOCK FOR LOGIN LOGIC
        user, user_type, user_name = None, None, None
        potential_student = Student.query.filter((Student.matric_number == username_or_email) | (Student.email == username_or_email)).first()
        if potential_student and potential_student.check_password(password):
            user, user_type, user_name = potential_student, "student", f"{potential_student.first_name} {potential_student.last_name}"
        else:
            potential_lecturer = Lecturer.query.filter_by(email=username_or_email).first()
            if potential_lecturer and potential_lecturer.check_password(password):
                user, user_type, user_name = potential_lecturer, "lecturer", f"{potential_lecturer.first_name} {potential_lecturer.last_name}"

        if user and user_type:
            additional_claims = {"user_type": user_type, "user_name": user_name}
            access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
            app.logger.info(f"Login successful for {user_type}: {username_or_email} (ID: {user.id})")
            return jsonify(success=True, access_token=access_token, user_type=user_type, user_name=user_name, user_id=user.id), 200
        else:
            app.logger.warn(f"Login failed for: {username_or_email}")
            return jsonify({"success": False, "message": "Invalid credentials or user not found."}), 401
    except Exception as e:
        # Log the actual error that's causing the 500
        app.logger.error(f"An unexpected error occurred during login for {username_or_email}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "An internal server error occurred during login. Please try again later."}), 500


@app.route('/api/students/forgot-password', methods=['POST'])
def student_forgot_password():
    data = request.get_json()
    if not data: return jsonify({"success": False, "message": "Request body must be JSON."}), 400
    matric_number = data.get('matric_number')
    if not matric_number: return jsonify({"success": False, "message": "Matriculation number is required."}), 400
    student = Student.query.filter_by(matric_number=matric_number).first()
    if not student:
        app.logger.info(f"Forgot password attempt for non-existent matric_number: {matric_number}")
        return jsonify({"success": True, "message": "If an account with that matriculation number exists, password reset instructions have been sent to the registered email address."}), 200
    if not student.email:
        app.logger.error(f"Student {matric_number} (ID: {student.id}) has no email address for password reset.")
        return jsonify({"success": True, "message": "If an account with that matriculation number exists and has a registered email, password reset instructions have been sent."}), 200
    try:
        temp_password = generate_random_numeric_password(8)
        student.set_password(temp_password)
        db.session.commit()
        subject = "Your Password Reset for Crawford Advising Portal"
        sender_email = app.config.get('MAIL_DEFAULT_SENDER', 'noreply@yourdomain.com')
        email_body = f"Hello {student.first_name},\n\nYour password for the Crawford University Academic Advising Portal has been temporarily reset.\n\nYour temporary password is: {temp_password}\n\nPlease log in using this temporary password and change it immediately via your profile settings.\n\nIf you did not request this password reset, please contact support.\n\nRegards,\nCrawford University Advising Team"
        msg = Message(subject, sender=sender_email, recipients=[student.email], body=email_body)
        mail.send(msg)
        app.logger.info(f"Password reset email sent to student: {student.email} for matric_number: {matric_number}")
        return jsonify({"success": True, "message": "Password reset instructions have been sent to your registered email address."}), 200
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Error during password reset for matric_number {matric_number}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "An error occurred while attempting to reset your password. Please try again later."}), 500

@app.route('/api/me/change-password', methods=['POST']) # <<<--- IMPLEMENTED THIS ENDPOINT
@jwt_required()
def change_my_password():
    user, user_type = get_typed_user_from_jwt_v2()

    if not user:
        return jsonify({"success": False, "message": "Authentication required. User not found in token."}), 401

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Request body must be JSON."}), 400

    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password') # Frontend sends this, backend should re-validate

    if not all([current_password, new_password, confirm_password]):
        return jsonify({"success": False, "message": "Current password, new password, and confirmation are required."}), 400

    if not user.check_password(current_password):
        app.logger.warn(f"Failed password change attempt for {user_type} ID {user.id}: Incorrect current password.")
        return jsonify({"success": False, "message": "Incorrect current password."}), 400

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "New password and confirmation do not match."}), 400

    if len(new_password) < 7:
        return jsonify({"success": False, "message": "New password must be at least 7 characters long."}), 400

    if user.check_password(new_password): # Check if new password is same as old
        return jsonify({"success": False, "message": "New password cannot be the same as the current password."}), 400

    try:
        user.set_password(new_password)
        db.session.commit()
        app.logger.info(f"Password changed successfully for {user_type} ID {user.id}.")
        return jsonify({"success": True, "message": "Password changed successfully. Please log in again with your new password for security."}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error changing password for {user_type} ID {user.id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "An error occurred while changing your password."}), 500

# --- Student APIs ---
@app.route('/api/student/data', methods=['GET'])
@jwt_required()
def get_student_dashboard_data():
    user, user_type = get_typed_user_from_jwt_v2()
    if not user or user_type != 'student': return jsonify({"success": False, "message": "Authentication failed or not a student."}), 401
    degree_data = {"name": "N/A", "faculty": "N/A"}
    if hasattr(user, 'degree') and user.degree:
        degree_data["name"] = user.degree.name
        if hasattr(user.degree, 'faculty') and user.degree.faculty: degree_data["faculty"] = user.degree.faculty
    student_info = {"id": user.id, "name": f"{user.first_name} {user.last_name}", "matric": user.matric_number, "email": user.email, "gpa": user.gpa, "degree": degree_data}
    advisor_info = None
    if hasattr(user, 'advisor') and user.advisor:
        advisor_info = {"name": f"{user.advisor.first_name} {user.advisor.last_name}", "email": user.advisor.email, "department": user.advisor.department, "office": user.advisor.office_location}
    try:
        resources_query = AdvisingResource.query.order_by(AdvisingResource.title).all()
        resources = [{"id": res.id, "title": res.title, "description": res.description, "url": res.url, "category": res.category} for res in resources_query]
    except Exception as e:
        app.logger.error(f"Error fetching advising resources: {str(e)}", exc_info=True); resources = []
    current_courses_placeholder = [{"code": "INFO101", "title": "Intro to University Life", "units": 1, "status": "Required"}]
    return jsonify(success=True, student_info=student_info, advisor_info=advisor_info, courses=current_courses_placeholder, resources=resources), 200

@app.route('/api/student/results', methods=['GET'])
@jwt_required()
def student_official_results():
    user, user_type = get_typed_user_from_jwt_v2()
    if not user or user_type != 'student': return jsonify({"success": False, "message": "Authentication failed or not a student."}), 401
    app.logger.info(f"Fetching official results for student ID: {user.id}")
    try:
        student_results_query = db.session.query(Result.grade, Result.semester, Result.gpa.label('grade_points'), Course.code.label('course_code'), Course.title.label('course_title'), Course.units.label('course_units')).join(Course, Result.course_id == Course.id).filter(Result.student_id == user.id).order_by(Result.semester.desc(), Course.code.asc()).all()
        results_data = [{"grade": res.grade, "semester": res.semester, "grade_points": res.grade_points, "course_code": res.course_code, "course_title": res.course_title, "course_units": res.course_units} for res in student_results_query]
        return jsonify({"success": True, "results": results_data}), 200
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Error fetching results for student ID {user.id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "An error occurred while fetching results."}), 500

# --- Lecturer APIs ---
@app.route('/api/lecturer/data', methods=['GET'])
@jwt_required()
def get_lecturer_dashboard_data():
    user, user_type = get_typed_user_from_jwt_v2()
    if not user or user_type != 'lecturer': return jsonify({"success": False, "message": "Authentication failed or not a lecturer."}), 401
    app.logger.info(f"Fetching dashboard data for lecturer ID: {user.id}")
    try:
        lecturer_info = {"id": user.id, "name": f"{user.first_name} {user.last_name}", "email": user.email, "department": user.department, "office_location": user.office_location}
        advisees_data = []
        if hasattr(user, 'advisees') and user.advisees:
            for student_advisee in user.advisees:
                degree_name = student_advisee.degree.name if student_advisee.degree else "N/A"
                advisees_data.append({
                    "id": student_advisee.id, "name": f"{student_advisee.first_name} {student_advisee.last_name}",
                    "matric_number": student_advisee.matric_number, "email": student_advisee.email,
                    "degree": degree_name, "gpa": student_advisee.gpa if student_advisee.gpa is not None else "N/A",
                    "guardian_name": student_advisee.guardian_name, "guardian_email": student_advisee.guardian_email,
                    "guardian_phone": student_advisee.guardian_phone, "guardian_relationship": student_advisee.guardian_relationship
                })
        resources_query = AdvisingResource.query.order_by(AdvisingResource.title).all()
        resources = [{"id": res.id, "title": res.title, "description": res.description, "url": res.url, "category": res.category} for res in resources_query]
        return jsonify(success=True, lecturer_info=lecturer_info, advisees=advisees_data, resources=resources), 200
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Error fetching data for L.ID {user.id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "An error occurred while fetching lecturer data."}), 500

@app.route('/api/lecturer/advisees/<int:advisee_id>/results', methods=['GET'])
@jwt_required()
def get_advisee_results_for_lecturer(advisee_id):
    lecturer, user_type = get_typed_user_from_jwt_v2()
    if not lecturer or user_type != 'lecturer': return jsonify({"success": False, "message": "Authentication failed or not a lecturer."}), 401
    advisee = db.session.get(Student, advisee_id)
    if not advisee: return jsonify({"success": False, "message": "Advisee (student) not found."}), 404
    if advisee.advisor_id != lecturer.id:
        app.logger.warn(f"Lecturer {lecturer.id} access attempt for non-advisee {advisee_id} results.")
        return jsonify({"success": False, "message": "You can only view results for your own advisees."}), 403
    app.logger.info(f"Lecturer ID: {lecturer.id} fetching results for advisee ID: {advisee_id}")
    try:
        student_results_query = db.session.query(Result.grade, Result.semester, Result.gpa.label('grade_points'), Course.code.label('course_code'), Course.title.label('course_title'), Course.units.label('course_units')).join(Course, Result.course_id == Course.id).filter(Result.student_id == advisee_id).order_by(Result.semester.desc(), Course.code.asc()).all()
        results_data = [{"grade": res.grade, "semester": res.semester, "grade_points": res.grade_points, "course_code": res.course_code, "course_title": res.course_title, "course_units": res.course_units} for res in student_results_query]
        student_name = f"{advisee.first_name} {advisee.last_name} ({advisee.matric_number})"
        return jsonify({"success": True, "student_name": student_name, "results": results_data}), 200
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Error fetching results for advisee {advisee_id} by L.{lecturer.id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "An error occurred while fetching advisee results."}), 500

@app.route('/api/lecturer/submit-grade', methods=['POST'])
@jwt_required()
def submit_grade():
    user, user_type = get_typed_user_from_jwt_v2()
    if not user or user_type != 'lecturer': return jsonify({"success": False, "message": "Only lecturers can submit grades."}), 403
    data = request.get_json()
    required_fields = ['student_id', 'course_id', 'grade', 'semester']
    if not data or not all(k in data for k in required_fields):
        missing = [k for k in required_fields if k not in data]; return jsonify({"success": False, "message": f"Missing required fields: {', '.join(missing)}."}), 400
    try:
        student_id, course_id = int(data['student_id']), int(data['course_id'])
        grade, semester_str, gpa_points = data['grade'], data['semester'], data.get('gpa')
        target_student, target_course = db.session.get(Student, student_id), db.session.get(Course, course_id)
        if not target_student: return jsonify({"success": False, "message": f"Student with ID {student_id} not found."}), 404
        if not target_course: return jsonify({"success": False, "message": f"Course with ID {course_id} not found."}), 404
        existing_result = Result.query.filter_by(student_id=student_id, course_id=course_id, semester=semester_str).first()
        if existing_result:
            app.logger.warn(f"Attempt to submit duplicate result for S_ID:{student_id}, C_ID:{course_id}, Sem:{semester_str}")
            return jsonify({"success": False, "message": f"A result for course {target_course.code} in semester {semester_str} already exists for student {target_student.matric_number}."}), 409
        new_result = Result(student_id=student_id, course_id=course_id, grade=grade, semester=semester_str, gpa=float(gpa_points) if gpa_points is not None else None)
        db.session.add(new_result); db.session.commit()
        app.logger.info(f"Lecturer ID {user.id} submitted grade '{grade}' for S_ID:{student_id}, C_ID:{course_id}, Sem:'{semester_str}'")
        return jsonify({"success": True, "message": "Grade submitted successfully."}), 201
    except ValueError:
        db.session.rollback(); app.logger.error(f"ValueError grade submission by L.{user.id}. Data: {data}", exc_info=True)
        return jsonify({"success": False, "message": "Invalid data format for student_id, course_id, or gpa."}), 400
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Error submitting grade by L.{user.id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Failed to submit grade due to a server error."}), 500

@app.route('/api/advisees/<int:advisee_id>/contact-guardian', methods=['POST'])
@jwt_required()
def contact_guardian(advisee_id):
    lecturer, user_type = get_typed_user_from_jwt_v2()
    if not lecturer or user_type != 'lecturer': return jsonify({"success": False, "message": "Authentication failed or not a lecturer."}), 401
    advisee = db.session.get(Student, advisee_id)
    if not advisee: return jsonify({"success": False, "message": "Advisee (student) not found."}), 404
    if advisee.advisor_id != lecturer.id:
        app.logger.warn(f"Lecturer {lecturer.id} attempt to contact guardian for non-advisee student {advisee_id}")
        return jsonify({"success": False, "message": "You are not authorized to contact the guardian for this student."}), 403
    if not advisee.guardian_email:
        app.logger.info(f"Attempt to contact guardian for student {advisee_id}, but no guardian email is registered.")
        return jsonify({"success": False, "message": f"No guardian email registered for {advisee.first_name} {advisee.last_name}."}), 400
    data = request.get_json()
    if not data: return jsonify({"success": False, "message": "Request body must be JSON."}), 400
    message_body_from_lecturer = data.get('message_body')
    email_subject_from_lecturer = data.get('subject', f"Regarding your ward, {advisee.first_name} {advisee.last_name}")
    is_urgent = data.get('is_urgent', False)
    if not message_body_from_lecturer or not message_body_from_lecturer.strip():
        return jsonify({"success": False, "message": "Message body cannot be empty."}), 400
    try:
        sender_email = app.config.get('MAIL_DEFAULT_SENDER', ('Crawford Advising', 'noreply@yourdomain.com'))
        subject_line = "URGENT: " + email_subject_from_lecturer if is_urgent else email_subject_from_lecturer
        email_html_body = f"""<p>Dear {advisee.guardian_name or 'Guardian'},</p><p>This message is from {lecturer.first_name} {lecturer.last_name}, the academic advisor for your ward, {advisee.first_name} {advisee.last_name} (Matric No: {advisee.matric_number}), at Crawford University.</p><hr><p><strong>Message:</strong></p><p>{message_body_from_lecturer.replace(os.linesep, '<br>')}</p><hr><p>If you have any questions, please feel free to reply to this email or contact the advising office.</p><p>Regards,<br>{lecturer.first_name} {lecturer.last_name}<br>{lecturer.department}<br>Crawford University</p>"""
        email_plain_body = f"Dear {advisee.guardian_name or 'Guardian'},\n\nThis message is from {lecturer.first_name} {lecturer.last_name}, the academic advisor for your ward, {advisee.first_name} {advisee.last_name} (Matric No: {advisee.matric_number}), at Crawford University.\n\nMessage:\n{message_body_from_lecturer}\n\nIf you have any questions, please feel free to reply to this email or contact the advising office.\n\nRegards,\n{lecturer.first_name} {lecturer.last_name}\n{lecturer.department}\nCrawford University"
        msg = Message(subject=subject_line, sender=sender_email, recipients=[advisee.guardian_email], body=email_plain_body, html=email_html_body)
        mail.send(msg)
        contact_note_content = f"Contacted guardian ({advisee.guardian_name or 'N/A'}, {advisee.guardian_email}) regarding: {email_subject_from_lecturer}. Message snippet: {message_body_from_lecturer[:100]}..."
        if is_urgent: contact_note_content = "[URGENT] " + contact_note_content
        new_log_note = AdvisingNote(content=contact_note_content, student_id=advisee_id, lecturer_id=user.id)
        db.session.add(new_log_note); db.session.commit()
        app.logger.info(f"Lecturer {user.id} sent email to guardian of student {advisee_id}. Urgent: {is_urgent}")
        return jsonify({"success": True, "message": f"Email successfully sent to the guardian of {advisee.first_name} {advisee.last_name}."}), 200
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Error contacting guardian for S_ID {advisee_id} by L.{user.id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "An error occurred while attempting to contact the guardian."}), 500

# --- Notes API ---
@app.route('/api/students/<int:student_id>/notes', methods=['GET'])
@jwt_required()
def get_student_advising_notes(student_id):
    user, user_type = get_typed_user_from_jwt_v2()
    if not user: return jsonify({"success": False, "message": "Authentication required."}), 401
    target_student = db.session.get(Student, student_id)
    if not target_student: return jsonify({"success": False, "message": "Student not found."}), 404
    is_student_self = (user_type == 'student' and user.id == student_id)
    is_lecturer_advisor = (user_type == 'lecturer' and target_student.advisor_id == user.id)
    if not (is_student_self or is_lecturer_advisor):
        app.logger.warn(f"Unauthorized attempt to access notes. User {user.id} ({user_type}) for student {student_id}.")
        return jsonify({"success": False, "message": "You are not authorized to view these notes."}), 403
    app.logger.info(f"Fetching notes for S_ID: {student_id} by {user_type} ID: {user.id}")
    try:
        notes_query = db.session.query(AdvisingNote.id, AdvisingNote.content, AdvisingNote.created_at, AdvisingNote.updated_at, (Lecturer.first_name + " " + Lecturer.last_name).label("author_name")).join(Lecturer, AdvisingNote.lecturer_id == Lecturer.id).filter(AdvisingNote.student_id == student_id).order_by(AdvisingNote.created_at.desc()).all()
        notes_data = [{"id": note.id, "content": note.content, "created_at": note.created_at.isoformat() if note.created_at else None, "updated_at": note.updated_at.isoformat() if note.updated_at else None, "author_name": note.author_name} for note in notes_query]
        return jsonify({"success": True, "notes": notes_data}), 200
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Error fetching notes for S_ID {student_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "An error occurred while fetching advising notes."}), 500

@app.route('/api/students/<int:student_id>/notes', methods=['POST'])
@jwt_required()
def add_advising_note_for_student(student_id):
    user, user_type = get_typed_user_from_jwt_v2()
    if not user or user_type != 'lecturer': return jsonify({"success": False, "message": "Only lecturers can add advising notes."}), 403
    data = request.get_json(); content = data.get('content')
    if not content or not content.strip(): return jsonify({"success": False, "message": "Note content is required and cannot be empty."}), 400
    target_student = db.session.get(Student, student_id)
    if not target_student: return jsonify({"success": False, "message": "Student not found."}), 404
    if target_student.advisor_id != user.id:
        app.logger.warn(f"Lecturer {user.id} attempt to add note for non-advisee student {student_id}")
        return jsonify({"success": False, "message": "You can only add notes for your own advisees."}), 403
    try:
        new_note = AdvisingNote(content=content, student_id=student_id, lecturer_id=user.id)
        db.session.add(new_note); db.session.commit()
        note_data = {"id": new_note.id, "content": new_note.content, "created_at": new_note.created_at.isoformat(), "updated_at": new_note.updated_at.isoformat(), "author_name": f"{user.first_name} {user.last_name}", "student_id": new_note.student_id}
        app.logger.info(f"Lecturer {user.id} added note for student {student_id}")
        return jsonify({"success": True, "message": "Note added successfully.", "note": note_data}), 201
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Error adding note for S_ID {student_id} by L.{user.id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Failed to add note."}), 500

# --- Resources API ---
@app.route('/api/resources', methods=['GET'])
def get_all_advising_resources():
    app.logger.info("Fetching all advising resources.")
    try:
        resources_query = AdvisingResource.query.order_by(AdvisingResource.category, AdvisingResource.title).all()
        resources_data = [{"id": resource.id, "title": resource.title, "description": resource.description, "url": resource.url, "category": resource.category} for res in resources_query]
        return jsonify({"success": True, "resources": resources_data}), 200
    except Exception as e:
        app.logger.error(f"Error fetching all advising resources: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "An error occurred while fetching resources."}), 500

# --- CLI Commands ---
try:
    from seed import seed_data_command
    app.cli.add_command(seed_data_command)
except ImportError: app.logger.info("Skipping seed command registration (seed.py not found or import error)")

# --- Global Error Handlers ---
@app.errorhandler(404)
def not_found_error(error): return jsonify({"success": False, "message": "Resource not found."}), 404
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback(); app.logger.error(f"Internal Server Error: {str(error)}", exc_info=True)
    return jsonify({"success": False, "message": "An internal server error occurred."}), 500
@app.errorhandler(400)
def bad_request_error(error):
    message = error.description if hasattr(error, 'description') and error.description else "Bad request."
    return jsonify({"success": False, "message": message}), 400

# --- Main Execution ---
if __name__ == '__main__':
    print("Starting Flask development server...")
    app.run(debug=True)
