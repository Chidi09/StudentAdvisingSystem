# backend/migrate_to_firebase.py

import os
import sys
import json
from datetime import datetime
from werkzeug.security import generate_password_hash # For creating dummy passwords if needed

# Add the backend directory to the Python path
# This allows importing app and models correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import Flask # Import Flask to create a dummy app context
from extensions import db, jwt, mail, cors # Import extensions for app initialization

# Import ALL Models
from models.degree import Degree
from models.course import Course
from models.student import Student
from models.lecturer import Lecturer
from models.advising_resource import AdvisingResource
from models.note import AdvisingNote
from models.enrollment import Enrollment
from models.result import Result

# --- Flask App Initialization (for DB context) ---
# Create a minimal Flask app instance to get the SQLAlchemy DB context
# This is crucial for querying your existing PostgreSQL/SQLite database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/default_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-super-secret-key-change-me') # JWT is not used for Firebase Auth
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.mailtrap.io')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 2525))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your_mailtrap_username')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your_mailtrap_password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@crawford.edu.ng')

db.init_app(app)
jwt.init_app(app)
mail.init_app(app)
cors.init_app(app) # Initialize CORS

# --- Firebase Admin SDK Initialization ---
try:
    cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "firebase-admin.json"))
    firebase_admin.initialize_app(cred)
    firestore_db = firestore.client()
    print("🔥 Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing Firebase Admin SDK: {e}")
    print("Please ensure 'firebase-admin.json' is in the 'backend' directory and is valid.")
    sys.exit(1)

# --- Helper to add/update document in Firestore ---
def add_to_firestore(collection_name, doc_id, data):
    try:
        firestore_db.collection(collection_name).document(str(doc_id)).set(data)
        # print(f"  ✅ Added/Updated {collection_name}/{doc_id}")
    except Exception as e:
        print(f"  ❌ Failed to add/update {collection_name}/{doc_id}: {e}")

# --- Dummy Data for empty tables ---
# Define a mapping for grades to GPA points (standard 5.0 scale)
GRADE_TO_GPA = {
    'A': 5.0, 'B': 4.0, 'C': 3.0, 'D': 2.0, 'E': 1.0, 'F': 0.0,
    'A+': 5.0, 'A-': 4.7, 'B+': 4.3, 'B-': 3.7, 'C+': 3.3, 'C-': 2.7,
    'D+': 2.3, 'D-': 1.7, 'E+': 1.3, 'E-': 0.7, 'F+': 0.3, 'F-': 0.0
}

def get_gpa_from_grade(grade):
    return GRADE_TO_GPA.get(grade.upper().strip(), 0.0)

def create_dummy_data():
    print("\n--- Creating Dummy Data for Empty Tables ---")
    dummy_data = {}

    # Dummy Degree
    degree_name = "BSc Computer Science"
    degree = Degree.query.filter_by(name=degree_name).first()
    if not degree:
        degree = Degree(name=degree_name, faculty="Faculty of Computing and Mathematical Sciences")
        db.session.add(degree)
        db.session.commit()
        print(f"  Created dummy Degree: {degree_name}")
    dummy_data['degree'] = degree

    # Dummy Lecturer
    lecturer_email = "lecturer@example.com"
    lecturer = Lecturer.query.filter_by(email=lecturer_email).first()
    if not lecturer:
        lecturer = Lecturer(
            first_name="Test",
            last_name="Lecturer",
            email=lecturer_email,
            department="Computer Science",
            office_location="A101",
            password_hash=generate_password_hash("password123") # Dummy password
        )
        db.session.add(lecturer)
        db.session.commit()
        print(f"  Created dummy Lecturer: {lecturer_email}")
    dummy_data['lecturer'] = lecturer

    # Dummy Student
    student_email = "student@example.com"
    student = Student.query.filter_by(email=student_email).first()
    if not student:
        student = Student(
            first_name="Test",
            last_name="Student",
            matric_number="CST/00/001",
            email=student_email,
            password_hash=generate_password_hash("password123"), # Dummy password
            degree_id=degree.id,
            gpa=0.0,
            advisor_id=lecturer.id,
            dob="2000-01-01",
            gender="Male",
            phone_number="08012345678",
            address="123 University Rd",
            guardian_name="Test Guardian",
            guardian_email="guardian@example.com",
            guardian_phone="09098765432",
            guardian_relationship="Parent"
        )
        db.session.add(student)
        db.session.commit()
        print(f"  Created dummy Student: {student_email}")
    dummy_data['student'] = student

    # Dummy Courses (from your provided list)
    provided_courses = [
        {"code": "CSC 305", "title": "Data Structure and Algorithm", "units": 3, "status": "E", "level": 300, "semester": 1},
        {"code": "CSC 307", "title": "Database Design and Management", "units": 3, "status": "C", "level": 300, "semester": 1},
        {"code": "CSC 309", "title": "Automata Theory, Compatibility and Formal Languages", "units": 2, "status": "C", "level": 300, "semester": 1},
        {"code": "CSC 311", "title": "Discrete Mathematics", "units": 3, "status": "E", "level": 300, "semester": 1},
        {"code": "CSC 317", "title": "Computer Architecture", "units": 3, "status": "C", "level": 300, "semester": 1},
        {"code": "CSC 319", "title": "Operating System II", "units": 3, "status": "C", "level": 300, "semester": 1},
        {"code": "CSC 323", "title": "Compiler Construction", "units": 3, "status": "C", "level": 300, "semester": 1},
        {"code": "EDS 301", "title": "Entrepreneurial Development Studies III", "units": 2, "status": "C", "level": 300, "semester": 1},
        {"code": "CSC 214", "title": "System Analysis and Design", "units": 3, "status": "C", "level": 200, "semester": 2}, # Adjusted level
        {"code": "CSC 304", "title": "Queuing Systems", "units": 3, "status": "C", "level": 300, "semester": 2},
        {"code": "CSC 306", "title": "Human Computer Interaction", "units": 3, "status": "E", "level": 300, "semester": 2},
        {"code": "CSC 308", "title": "Computer Hardware and Embedded Systems", "units": 3, "status": "C", "level": 300, "semester": 2},
        {"code": "CSC 314", "title": "Multimedia Signal Processing and Communication", "units": 3, "status": "C", "level": 300, "semester": 2},
        {"code": "CSC 399", "title": "Industrial Attachment", "units": 6, "status": "C", "level": 300, "semester": 2}
    ]
    dummy_data['courses'] = []
    for course_data in provided_courses:
        course = Course.query.filter_by(code=course_data['code']).first()
        if not course:
            course = Course(
                code=course_data['code'],
                title=course_data['title'],
                units=course_data['units'],
                status=course_data['status'],
                level=course_data['level'],
                semester=course_data['semester'] # 1 or 2
            )
            db.session.add(course)
            db.session.commit()
            print(f"  Created dummy Course: {course.code}")
        dummy_data['courses'].append(course)

    # Dummy Results for the student
    provided_results = [
        {"course_code": "CSC 305", "grade": "B", "semester": "2023/2024 - Semester 1", "score": 60},
        {"course_code": "CSC 307", "grade": "E", "semester": "2023/2024 - Semester 1", "score": 40},
        {"course_code": "CSC 309", "grade": "C", "semester": "2023/2024 - Semester 1", "score": 50},
        {"course_code": "CSC 311", "grade": "B", "semester": "2023/2024 - Semester 1", "score": 60},
        {"course_code": "CSC 317", "grade": "D", "semester": "2023/2024 - Semester 1", "score": 45},
        {"course_code": "CSC 319", "grade": "C", "semester": "2023/2024 - Semester 1", "score": 56},
        {"course_code": "CSC 323", "grade": "B", "semester": "2023/2024 - Semester 1", "score": 60},
        {"course_code": "EDS 301", "grade": "B", "semester": "2023/2024 - Semester 1", "score": 66},
        {"course_code": "CSC 214", "grade": "C", "semester": "2023/2024 - Semester 2", "score": 53},
        {"course_code": "CSC 304", "grade": "D", "semester": "2023/2024 - Semester 2", "score": 46},
        {"course_code": "CSC 306", "grade": "B", "semester": "2023/2024 - Semester 2", "score": 65},
        {"course_code": "CSC 308", "grade": "C", "semester": "2023/2024 - Semester 2", "score": 51},
        {"course_code": "CSC 314", "grade": "B", "semester": "2023/2024 - Semester 2", "score": 67},
        {"course_code": "CSC 399", "grade": "DEX", "semester": "2023/2024 - Semester 2", "score": 0} # DEX for Industrial Attachment
    ]
    for res_data in provided_results:
        course = Course.query.filter_by(code=res_data['course_code']).first()
        if course:
            result = Result.query.filter_by(
                student_id=student.id,
                course_id=course.id,
                semester=res_data['semester']
            ).first()
            if not result:
                result = Result(
                    student_id=student.id,
                    course_id=course.id,
                    grade=res_data['grade'],
                    semester=res_data['semester'],
                    gpa=get_gpa_from_grade(res_data['grade']) # Calculate GPA based on grade
                )
                db.session.add(result)
                db.session.commit()
                print(f"  Created dummy Result for {student.email} in {course.code}")

    # Dummy Advising Note
    note = AdvisingNote.query.filter_by(student_id=student.id, lecturer_id=lecturer.id).first()
    if not note:
        note = AdvisingNote(
            content="Initial advising session: Discussed course selection and academic goals.",
            student_id=student.id,
            lecturer_id=lecturer.id,
            created_at=datetime.utcnow()
        )
        db.session.add(note)
        db.session.commit()
        print("  Created dummy Advising Note.")

    # Dummy Advising Resource
    resource_title = "Student Handbook"
    resource = AdvisingResource.query.filter_by(title=resource_title).first()
    if not resource:
        resource = AdvisingResource(
            title=resource_title,
            description="Official university student handbook with policies and guidelines.",
            url="https://example.com/student-handbook",
            category="General"
        )
        db.session.add(resource)
        db.session.commit()
        print(f"  Created dummy Advising Resource: {resource_title}")

    return dummy_data

# --- Main Migration Logic ---
def migrate_data():
    with app.app_context():
        # Ensure dummy data exists if tables are empty
        dummy_data = create_dummy_data()
        default_student_uid = None
        default_lecturer_uid = None

        # 1. Migrate Degrees
        print("\n--- Migrating Degrees ---")
        degrees = Degree.query.all()
        for degree in degrees:
            doc_data = {
                "name": degree.name,
                "faculty": degree.faculty
            }
            add_to_firestore("degrees", degree.id, doc_data)

        # 2. Migrate Lecturers (and create users in 'users' collection with role 'lecturer')
        print("\n--- Migrating Lecturers ---")
        lecturers = Lecturer.query.all()
        for lecturer in lecturers:
            # We use the lecturer's email as a unique identifier for Firebase Auth
            # For simplicity, we'll generate a UID for them here if not already linked to Firebase Auth
            # In a real scenario, you'd link existing users to Firebase Auth
            # For this migration, we'll use their DB ID as the Firestore Document ID
            lecturer_uid = f"lecturer_{lecturer.id}" # Using a prefix to avoid collision if IDs overlap with students
            # Or, if you want to link to actual Firebase Auth UIDs, you'd fetch them here.
            # For now, let's use a consistent ID.
            
            # If the dummy lecturer was created, use its UID for consistency
            if lecturer.email == "lecturer@example.com" and hasattr(dummy_data['lecturer'], 'id'):
                lecturer_uid = f"lecturer_{dummy_data['lecturer'].id}"
                default_lecturer_uid = lecturer_uid # Store for later use

            user_doc_data = {
                "name": f"{lecturer.first_name} {lecturer.last_name}",
                "email": lecturer.email,
                "department": lecturer.department,
                "office_location": lecturer.office_location,
                "role": "lecturer"
            }
            add_to_firestore("users", lecturer_uid, user_doc_data)

        # 3. Migrate Students (and create users in 'users' collection with role 'student')
        print("\n--- Migrating Students ---")
        students = Student.query.all()
        for student in students:
            # Similar to lecturers, use a consistent UID for Firestore Document ID
            student_uid = f"student_{student.id}"
            if student.email == "student@example.com" and hasattr(dummy_data['student'], 'id'):
                student_uid = f"student_{dummy_data['student'].id}"
                default_student_uid = student_uid # Store for later use

            user_doc_data = {
                "name": f"{student.first_name} {student.last_name}",
                "email": student.email,
                "matric_number": student.matric_number,
                "gpa": student.gpa,
                "role": "student",
                "dob": student.dob,
                "gender": student.gender,
                "phone_number": student.phone_number,
                "address": student.address,
                "guardian_name": student.guardian_name,
                "guardian_email": student.guardian_email,
                "guardian_phone": student.guardian_phone,
                "guardian_relationship": student.guardian_relationship
            }
            if student.degree:
                user_doc_data["degree"] = {
                    "id": student.degree.id,
                    "name": student.degree.name,
                    "faculty": student.degree.faculty
                }
            if student.advisor:
                user_doc_data["advisorId"] = f"lecturer_{student.advisor.id}" # Link to lecturer's Firestore UID
            add_to_firestore("users", student_uid, user_doc_data)

        # 4. Migrate Courses
        print("\n--- Migrating Courses ---")
        courses = Course.query.all()
        for course in courses:
            doc_data = {
                "code": course.code,
                "title": course.title,
                "units": course.units,
                "status": course.status,
                "level": course.level,
                "semester": course.semester
            }
            add_to_firestore("courses", course.id, doc_data)

        # 5. Migrate Enrollments (if you had any specific enrollment data beyond results)
        # Note: Your current Enrollment model doesn't have grade/gpa, Result model handles that.
        # So, for now, we'll just migrate basic enrollment records if they exist.
        print("\n--- Migrating Enrollments (if applicable) ---")
        enrollments = Enrollment.query.all()
        for enrollment in enrollments:
            doc_data = {
                "studentId": f"student_{enrollment.student_id}", # Link to student's Firestore UID
                "courseId": enrollment.course_id,
                "academic_year": enrollment.academic_year,
                "semester": enrollment.semester,
                "enrolled_at": enrollment.enrolled_at,
                "updated_at": enrollment.updated_at
            }
            add_to_firestore("enrollments", enrollment.id, doc_data)


        # 6. Migrate Results
        print("\n--- Migrating Results ---")
        results = Result.query.all()
        for result in results:
            doc_data = {
                "studentId": f"student_{result.student_id}", # Link to student's Firestore UID
                "courseId": result.course_id,
                "grade": result.grade,
                "semester": result.semester,
                "gpa": result.gpa
            }
            add_to_firestore("results", result.id, doc_data)

        # 7. Migrate Advising Notes
        print("\n--- Migrating Advising Notes ---")
        notes = AdvisingNote.query.all()
        for note in notes:
            doc_data = {
                "content": note.content,
                "studentId": f"student_{note.student_id}", # Link to student's Firestore UID
                "lecturerId": f"lecturer_{note.lecturer_id}", # Link to lecturer's Firestore UID
                "created_at": note.created_at,
                "updated_at": note.updated_at,
                "author_name": note.author.first_name + " " + note.author.last_name if note.author else "Unknown" # Denormalized for display
            }
            add_to_firestore("advising_notes", note.id, doc_data)

        # 8. Migrate Advising Resources
        print("\n--- Migrating Advising Resources ---")
        resources = AdvisingResource.query.all()
        for resource in resources:
            doc_data = {
                "title": resource.title,
                "description": resource.description,
                "url": resource.url,
                "category": resource.category
            }
            add_to_firestore("advising_resources", resource.id, doc_data)

        print("\n--- Data Migration to Firebase Firestore Complete! ---")
        print("Remember to create corresponding users in Firebase Authentication if you haven't already,")
        print("and ensure their UIDs match the Document IDs in the 'users' collection (e.g., student_1, lecturer_1).")
        print("For the dummy student/lecturer, their UIDs will be 'student_X' and 'lecturer_Y' where X/Y are their original DB IDs.")

if __name__ == "__main__":
    # To run this script, ensure your Flask app's database is accessible
    # and you have the firebase-admin.json key in the backend directory.
    # Run from your project root: python backend/migrate_to_firebase.py
    migrate_data()
