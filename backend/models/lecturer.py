# backend/models/lecturer.py
# --- Corrected Version ---
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash # Import hashing functions

class Lecturer(db.Model):
    __tablename__ = 'lecturers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    department = db.Column(db.String(150), nullable=True)
    office_location = db.Column(db.String(100), nullable=True) # Ensure this is used in app.py or remove if not needed
    password_hash = db.Column(db.String(255), nullable=True)

    # Relationship to advisees is now handled by the backref
    # from the 'Student.advisor' relationship.
    # The 'lecturer.advisees' attribute will be automatically available.
    # --- REMOVED THE FOLLOWING LINE ---
    # advisees = db.relationship('Student', foreign_keys='Student.advisor_id', backref='advisor')
    # --- END REMOVAL ---

    # Relationship to AdvisingNotes authored by this lecturer
    # 'note.author' will link back to this Lecturer object
    notes_authored = db.relationship('AdvisingNote', back_populates='author', lazy='dynamic')

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Checks if the submitted password matches the stored hash."""
        if not self.password_hash:
            return False # No password set
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Lecturer {self.first_name} {self.last_name}>'