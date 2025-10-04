from app import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # e.g., USD, EUR, INR
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', back_populates='company', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', back_populates='company', cascade='all, delete-orphan')
    approval_rules = db.relationship('ApprovalRule', back_populates='company', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert company to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'currency': self.currency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Company {self.name}>'