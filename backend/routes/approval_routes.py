from flask import Blueprint, request, jsonify
from app import db
from models.approval import ApprovalLog
from models.expense import Expense
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

approval_bp = Blueprint("approval_bp", __name__)

@approval_bp.route("/pending", methods=["GET"])
@jwt_required()
def pending():
    approver_id = get_jwt_identity()
    expenses = Expense.query.filter_by(current_approver_id=approver_id, status="Pending").all()
    return jsonify([{"id": e.id, "desc": e.description, "amount": e.amount} for e in expenses])

@approval_bp.route("/approve/<int:expense_id>", methods=["POST"])
@jwt_required()
def approve(expense_id):
    approver_id = get_jwt_identity()
    data = request.json
    log = ApprovalLog(
        expense_id=expense_id,
        approver_id=approver_id,
        status="Approved",
        comment=data.get("comment", ""),
        approved_at=datetime.now()
    )
    db.session.add(log)
    expense = Expense.query.get(expense_id)
    expense.status = "Approved"
    db.session.commit()
    return jsonify({"message": "Expense approved!"})

