from app import db
from datetime import datetime
import json

class ApprovalRule(db.Model):
    __tablename__ = 'approval_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', back_populates='approval_rules')
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Rule type: sequential, conditional, hybrid
    rule_type = db.Column(db.String(20), nullable=False)
    
    # Conditions stored as JSON
    # Example: {"percentage": 60, "specific_approvers": [1, 2], "operator": "OR"}
    conditions = db.Column(db.JSON, nullable=True)
    
    # Sequential approval steps (JSON array of approver IDs in order)
    # Example: [3, 5, 7] means Manager -> Finance -> Director
    approval_sequence = db.Column(db.JSON, nullable=True)
    
    # Minimum/Maximum amount thresholds
    min_amount = db.Column(db.Numeric(10, 2), nullable=True)
    max_amount = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Category filter
    category = db.Column(db.String(50), nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'description': self.description,
            'rule_type': self.rule_type,
            'conditions': self.conditions,
            'approval_sequence': self.approval_sequence,
            'min_amount': float(self.min_amount) if self.min_amount else None,
            'max_amount': float(self.max_amount) if self.max_amount else None,
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<ApprovalRule {self.name}>'


class ApprovalStep(db.Model):
    __tablename__ = 'approval_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Expense being approved
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False)
    expense = db.relationship('Expense', back_populates='approval_steps')
    
    # Approver
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approver = db.relationship('User', back_populates='approvals', foreign_keys=[approver_id])
    
    # Step details
    step_order = db.Column(db.Integer, nullable=False)  # Order in the approval sequence
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    comments = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    action_taken_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'expense_id': self.expense_id,
            'approver_id': self.approver_id,
            'approver_name': self.approver.full_name if self.approver else None,
            'approver_email': self.approver.email if self.approver else None,
            'step_order': self.step_order,
            'status': self.status,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'action_taken_at': self.action_taken_at.isoformat() if self.action_taken_at else None,
        }
    
    def __repr__(self):
        return f'<ApprovalStep {self.id} - Expense {self.expense_id}>'