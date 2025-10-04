from app import db

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Float)
    currency = db.Column(db.String(10))
    converted_amount = db.Column(db.Float)
    category = db.Column(db.String(100))
    description = db.Column(db.String(255))
    date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Pending")
    current_approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class ExpenseAttachment(db.Model):
    __tablename__ = 'expense_attachments'
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'))
    file_url = db.Column(db.String(255))
    ocr_text = db.Column(db.Text)

