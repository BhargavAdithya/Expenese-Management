from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, ApprovalRule
from datetime import datetime

rule_bp = Blueprint('rule', __name__)

@rule_bp.route('/', methods=['POST'])
@jwt_required()
def create_approval_rule():
    """
    Admin creates a new approval rule
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Only admins can create rules
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'rule_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate rule_type
        if data['rule_type'] not in ['sequential', 'conditional', 'hybrid']:
            return jsonify({'error': 'Invalid rule_type. Must be: sequential, conditional, or hybrid'}), 400
        
        # Validate sequential approval has approval_sequence
        if data['rule_type'] in ['sequential', 'hybrid']:
            if not data.get('approval_sequence'):
                return jsonify({'error': 'approval_sequence is required for sequential/hybrid rules'}), 400
        
        # Validate conditional approval has conditions
        if data['rule_type'] in ['conditional', 'hybrid']:
            if not data.get('conditions'):
                return jsonify({'error': 'conditions are required for conditional/hybrid rules'}), 400
        
        # Create rule
        rule = ApprovalRule(
            company_id=user.company_id,
            name=data['name'],
            description=data.get('description'),
            rule_type=data['rule_type'],
            conditions=data.get('conditions'),
            approval_sequence=data.get('approval_sequence'),
            min_amount=data.get('min_amount'),
            max_amount=data.get('max_amount'),
            category=data.get('category'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({
            'message': 'Approval rule created successfully',
            'rule': rule.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rule_bp.route('/', methods=['GET'])
@jwt_required()
def get_approval_rules():
    """
    Get all approval rules for the company
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        rules = ApprovalRule.query.filter_by(
            company_id=user.company_id
        ).order_by(ApprovalRule.created_at.desc()).all()
        
        return jsonify({
            'rules': [rule.to_dict() for rule in rules]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rule_bp.route('/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_approval_rule(rule_id):
    """
    Get single approval rule details
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        rule = ApprovalRule.query.get(rule_id)
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404
        
        # Check if rule belongs to user's company
        if rule.company_id != user.company_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'rule': rule.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rule_bp.route('/<int:rule_id>', methods=['PUT'])
@jwt_required()
def update_approval_rule(rule_id):
    """
    Admin updates an approval rule
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Only admins can update rules
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        rule = ApprovalRule.query.get(rule_id)
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404
        
        if rule.company_id != user.company_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            rule.name = data['name']
        if 'description' in data:
            rule.description = data['description']
        if 'rule_type' in data:
            if data['rule_type'] not in ['sequential', 'conditional', 'hybrid']:
                return jsonify({'error': 'Invalid rule_type'}), 400
            rule.rule_type = data['rule_type']
        if 'conditions' in data:
            rule.conditions = data['conditions']
        if 'approval_sequence' in data:
            rule.approval_sequence = data['approval_sequence']
        if 'min_amount' in data:
            rule.min_amount = data['min_amount']
        if 'max_amount' in data:
            rule.max_amount = data['max_amount']
        if 'category' in data:
            rule.category = data['category']
        if 'is_active' in data:
            rule.is_active = data['is_active']
        
        rule.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Approval rule updated successfully',
            'rule': rule.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rule_bp.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_approval_rule(rule_id):
    """
    Admin deletes an approval rule
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Only admins can delete rules
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        rule = ApprovalRule.query.get(rule_id)
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404
        
        if rule.company_id != user.company_id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({
            'message': 'Approval rule deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rule_bp.route('/<int:rule_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_rule_status(rule_id):
    """
    Admin toggles rule active status
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Only admins can toggle rules
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        rule = ApprovalRule.query.get(rule_id)
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404
        
        if rule.company_id != user.company_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Toggle status
        rule.is_active = not rule.is_active
        rule.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': f'Rule {"activated" if rule.is_active else "deactivated"} successfully',
            'rule': rule.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500