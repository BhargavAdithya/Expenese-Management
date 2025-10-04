from database import db  # <-- CHANGE THIS LINE
from datetime import datetime

class Company(db.Model):
    # ... (the rest of the file is unchanged)
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = db.relationship('User', back_populates='company', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', back_populates='company', cascade='all, delete-orphan')
    approval_rules = db.relationship('ApprovalRule', back_populates='company', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'currency': self.currency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
