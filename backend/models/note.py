# backend/models/note.py
from extensions import db
from datetime import datetime # Import datetime for timestamps

class AdvisingNote(db.Model):
    __tablename__ = 'advising_notes'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False) # Use Text for potentially long notes
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys to link the note to a student and a lecturer (author)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=False, index=True)

    # Relationships (for easy access from note object)
    # Allows accessing note.student and note.author
    student = db.relationship('Student', back_populates='notes')
    author = db.relationship('Lecturer', back_populates='notes_authored') # Changed name to 'author'

    def __repr__(self):
        return f'<AdvisingNote {self.id} for Student {self.student_id} by Lecturer {self.lecturer_id}>'