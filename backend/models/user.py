from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(50), default="Employee")
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    def __repr__(self):
        return f"<User {self.name}>"

