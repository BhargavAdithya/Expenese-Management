from database import db  # <-- CHANGE THIS LINE
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    # ... (the rest of the file is unchanged)
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', back_populates='users')
    
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    manager = db.relationship('User', remote_side=[id], backref='subordinates')
    
    is_manager_approver = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    expenses = db.relationship('Expense', back_populates='employee', foreign_keys='Expense.employee_id')
    approvals = db.relationship('ApprovalStep', back_populates='approver', foreign_keys='ApprovalStep.approver_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_company=False):
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'company_id': self.company_id,
            'manager_id': self.manager_id,
            'is_manager_approver': self.is_manager_approver,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_company and self.company:
            data['company'] = self.company.to_dict()
        return data
