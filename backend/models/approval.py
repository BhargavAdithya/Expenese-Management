from app import db

class ApprovalFlow(db.Model):
    __tablename__ = 'approval_flows'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    step_number = db.Column(db.Integer)
    approver_role = db.Column(db.String(50))
    is_manager_approver = db.Column(db.Boolean, default=False)

class ApprovalLog(db.Model):
    __tablename__ = 'approval_logs'
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'))
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(50))
    comment = db.Column(db.Text)
    approved_at = db.Column(db.DateTime)

