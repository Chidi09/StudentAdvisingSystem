# backend/models/student.py
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    matric_number = db.Column(db.String(20), unique=True, nullable=False)
    gpa = db.Column(db.Float, nullable=True) # Overall GPA for the student
    password_hash = db.Column(db.String(255), nullable=True)

    # Foreign Keys
    degree_id = db.Column(db.Integer, db.ForeignKey('degrees.id'), nullable=True)
    advisor_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=True)

    # --- Guardian Information ---
    guardian_name = db.Column(db.String(150), nullable=True)
    guardian_email = db.Column(db.String(120), nullable=True) # For sending emails
    guardian_phone = db.Column(db.String(30), nullable=True)  # Increased length for international
    guardian_relationship = db.Column(db.String(50), nullable=True) # e.g., Parent, Guardian, Sponsor

    # Relationships
    degree = db.relationship('Degree', backref=db.backref('students', lazy='select'))
    advisor = db.relationship('Lecturer', backref=db.backref('advisees', lazy='select')) # 'advisees' on Lecturer is a list
    enrollments = db.relationship('Enrollment', back_populates='student', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('AdvisingNote', back_populates='student', lazy='dynamic', cascade='all, delete-orphan')
    # Results are typically queried directly via student_id, but a relationship can be added if desired:
    # results = db.relationship('Result', backref='student_info', lazy='dynamic', cascade='all, delete-orphan')


    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Checks if the submitted password matches the stored hash."""
        if not self.password_hash:
            return False # No password set
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Student {self.matric_number} - {self.first_name} {self.last_name}>'
