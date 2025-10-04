from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')  # admin, manager, employee
    
    # Company relationship
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', back_populates='users')
    
    # Manager relationship (self-referential)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    manager = db.relationship('User', remote_side=[id], backref='subordinates')
    
    # Approval settings
    is_manager_approver = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    expenses = db.relationship('Expense', back_populates='employee', foreign_keys='Expense.employee_id')
    approvals = db.relationship('ApprovalStep', back_populates='approver', foreign_keys='ApprovalStep.approver_id')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_company=False):
        """Convert user to dictionary"""
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
            data['company'] = {
                'id': self.company.id,
                'name': self.company.name,
                'currency': self.company.currency
            }
        
        if self.manager:
            data['manager'] = {
                'id': self.manager.id,
                'full_name': self.manager.full_name,
                'email': self.manager.email
            }
        
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'