from app import db
from datetime import datetime

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Employee who submitted the expense
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee = db.relationship('User', back_populates='expenses', foreign_keys=[employee_id])
    
    # Company
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', back_populates='expenses')
    
    # Expense details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    original_currency = db.Column(db.String(10), nullable=False)  # Currency of the expense
    category = db.Column(db.String(50), nullable=False)  # Travel, Food, Office Supplies, etc.
    description = db.Column(db.Text, nullable=True)
    expense_date = db.Column(db.Date, nullable=False)
    
    # Receipt/OCR
    receipt_url = db.Column(db.String(500), nullable=True)
    vendor_name = db.Column(db.String(200), nullable=True)  # From OCR
    
    # Status tracking
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    
    # Approval tracking
    current_approval_step = db.Column(db.Integer, default=0)  # Which approval step is it at
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    approval_steps = db.relationship('ApprovalStep', back_populates='expense', cascade='all, delete-orphan')
    
    def to_dict(self, include_approvals=False):
        """Convert expense to dictionary"""
        data = {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name if self.employee else None,
            'company_id': self.company_id,
            'amount': float(self.amount),
            'original_currency': self.original_currency,
            'category': self.category,
            'description': self.description,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'receipt_url': self.receipt_url,
            'vendor_name': self.vendor_name,
            'status': self.status,
            'current_approval_step': self.current_approval_step,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_approvals:
            data['approval_steps'] = [step.to_dict() for step in self.approval_steps]
        
        return data
    
    def __repr__(self):
        return f'<Expense {self.id} - {self.amount} {self.original_currency}>'