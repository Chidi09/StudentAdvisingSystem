# backend/models/student.py
from extensions import db # Import the db instance from extensions.py

class Course(db.Model):
    __tablename__ = 'courses'
    enrollments = db.relationship ('Enrollment', back_populates='course', lazy='dynamic')
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, unique=True) # e.g., "CSC 101"
    title = db.Column(db.String(200), nullable=False) # e.g., "Introduction to Computer Science"
    units = db.Column(db.Integer, nullable=False) # e.g., 3
    status = db.Column(db.String(20), nullable=True) # Should have 20 or similar, NOT 1
    level = db.Column(db.Integer, nullable=True) # e.g., 100, 200, 300, 400
    semester = db.Column(db.Integer, nullable=True) # e.g., 1 (First), 2 (Second)

    # Relationships (defined later if needed, e.g., prerequisites, degrees offering this course)

    def __repr__(self):
        return f'<Course {self.code} - {self.title}>'