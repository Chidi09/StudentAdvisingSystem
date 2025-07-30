# backend/models/student.py
from extensions import db # Import the db instance from extensions.py

class Degree(db.Model):
    __tablename__ = 'degrees' # Optional: Define the table name explicitly

    id = db.Column(db.Integer, primary_key=True) # Auto-incrementing primary key
    name = db.Column(db.String(150), nullable=False, unique=True) # e.g., "BSc Computer Science"
    faculty = db.Column(db.String(150), nullable=True) # e.g., "Faculty of Natural and Applied Sciences"

    # Relationship (defined later if needed, e.g., students in this degree)
    # students = db.relationship('Student', backref='degree', lazy=True)

    def __repr__(self):
        # Optional: Return a string representation of the object
        return f'<Degree {self.name}>'