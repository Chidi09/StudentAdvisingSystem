# StudentAdvisingSystem/backend/models/result.py
from extensions import db # <<< इंश्योर करें कि यह इम्पोर्ट सही है

class Result(db.Model):
    __tablename__ = 'results' # Adding explicit table name for clarity

    id = db.Column(db.Integer, primary_key=True)
    # Ensure student_id references the primary key of your 'students' table correctly
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    # Ensure course_id references the primary key of your 'courses' table correctly
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    
    grade = db.Column(db.String(5), nullable=False)  # e.g., "A", "B+", "C"
    semester = db.Column(db.String(50), nullable=False)  # e.g., "2023/2024 - Semester 1" (as used in seed.py)
    gpa = db.Column(db.Float, nullable=True)  # Grade points for this specific course result

    # Optional: Relationships can be helpful for ORM-based access patterns
    # If your 'Student' model has a backref like 'results', define it here or there.
    # If your 'Course' model has a backref like 'results', define it here or there.
    # student = db.relationship('Student', backref=db.backref('student_results', lazy='dynamic')) # Example backref name
    # course = db.relationship('Course', backref=db.backref('course_results', lazy='dynamic'))   # Example backref name

    def __repr__(self):
        return f'<Result ID:{self.id} StudentID:{self.student_id} CourseID:{self.course_id} Grade:{self.grade} Semester:{self.semester}>'