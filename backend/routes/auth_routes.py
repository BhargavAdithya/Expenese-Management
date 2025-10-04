from flask import Blueprint, request, jsonify
from app import db
from models.user import User
from models.company import Company
from flask_jwt_extended import create_access_token
import requests, hashlib

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name = data["name"]
    email = data["email"]
    password = hashlib.sha256(data["password"].encode()).hexdigest()
    country = data["country"]

    # Fetch currency from REST Countries API
    res = requests.get("https://restcountries.com/v3.1/all?fields=name,currencies").json()
    currency = next(
        (list(c["currencies"].keys())[0] for c in res if c["name"]["common"] == country),
        "USD"
    )

    company = Company(name=f"{name}'s Company", country=country, currency=currency)
    db.session.add(company)
    db.session.commit()

    admin = User(name=name, email=email, password_hash=password, role="Admin", company_id=company.id)
    company.admin_id = admin.id
    db.session.add(admin)
    db.session.commit()

    token = create_access_token(identity=admin.id)
    return jsonify({"token": token, "message": "Admin and company created!"})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user or user.password_hash != hashlib.sha256(data["password"].encode()).hexdigest():
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "role": user.role})

