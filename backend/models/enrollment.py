# backend/models/enrollment.py
from extensions import db
from datetime import datetime

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    
    # Semester information
    academic_year = db.Column(db.String(9), nullable=False)  # E.g., "2023/2024"
    semester = db.Column(db.Integer, nullable=False)       # E.g., 1 for first, 2 for second

    # Grade and grade_points columns have been removed as Result model is the source of truth.

    # Timestamps
    enrolled_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (for easy access from an Enrollment object)
    # enrollment.student will give the Student object
    # enrollment.course will give the Course object
    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    # Ensure a student can only be enrolled in the same course once per specific semester/year
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', 'academic_year', 'semester', name='uq_student_course_semester'),)

    def __repr__(self):
        # Corrected indentation for the return statement.
        # Removed self.grade as it's no longer an attribute of this model.
        return f'<Enrollment StudentID:{self.student_id} CourseID:{self.course_id} Year:{self.academic_year} Sem:{self.semester}>'
