# backend/models/student.py
from extensions import db # Import the db instance from extensions.py

class AdvisingResource(db.Model):
    __tablename__ = 'advising_resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True) # Text allows longer content than String
    url = db.Column(db.String(255), nullable=True) # URL to the resource if applicable
    category = db.Column(db.String(50), nullable=True) # e.g., 'Form', 'Policy', 'Guide', 'Link'

    def __repr__(self):
        return f'<AdvisingResource {self.title}>'