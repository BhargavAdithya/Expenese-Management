from flask import Blueprint, request, jsonify
from app import db
from models.expense import Expense
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.currency_service import convert_currency
from datetime import datetime

expense_bp = Blueprint("expense_bp", __name__)

@expense_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_expense():
    user_id = get_jwt_identity()
    data = request.json

    converted = convert_currency(data["amount"], data["currency"], data["company_currency"])

    expense = Expense(
        employee_id=user_id,
        amount=data["amount"],
        currency=data["currency"],
        converted_amount=converted,
        category=data["category"],
        description=data["description"],
        date=datetime.strptime(data["date"], "%Y-%m-%d")
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify({"message": "Expense submitted successfully!"})

@expense_bp.route("/my", methods=["GET"])
@jwt_required()
def get_my_expenses():
    user_id = get_jwt_identity()
    expenses = Expense.query.filter_by(employee_id=user_id).all()
    return jsonify([{
        "id": e.id,
        "amount": e.amount,
        "status": e.status,
        "description": e.description
    } for e in expenses])

