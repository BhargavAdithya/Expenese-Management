from app import db

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    country = db.Column(db.String(120))
    currency = db.Column(db.String(10))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))

