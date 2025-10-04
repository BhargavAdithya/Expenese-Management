from flask import Blueprint, request, jsonify
from app import db
from models.approval import ApprovalFlow

rule_bp = Blueprint("rule_bp", __name__)

@rule_bp.route("/create", methods=["POST"])
def create_rule():
    data = request.json
    rule = ApprovalFlow(
        company_id=data["company_id"],
        step_number=data["step_number"],
        approver_role=data["approver_role"],
        is_manager_approver=data.get("is_manager_approver", False)
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify({"message": "Rule created!"})

