from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Expense, ApprovalStep, ApprovalRule
from datetime import datetime

approval_bp = Blueprint('approval', __name__)

@approval_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_approvals():
    """
    Get all expenses waiting for current user's approval
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Find approval steps where user is approver and status is pending
        approval_steps = ApprovalStep.query.filter_by(
            approver_id=user.id,
            status='pending'
        ).order_by(ApprovalStep.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        expenses_data = []
        for step in approval_steps.items:
            expense = step.expense
            expense_dict = expense.to_dict()
            expense_dict['approval_step'] = step.to_dict()
            
            # Convert to company currency
            if expense.original_currency != user.company.currency:
                from services.currency_service import CurrencyService
                currency_service = CurrencyService()
                expense_dict['converted_amount'] = currency_service.convert(
                    expense.amount,
                    expense.original_currency,
                    user.company.currency
                )
                expense_dict['company_currency'] = user.company.currency
            
            expenses_data.append(expense_dict)
        
        return jsonify({
            'pending_approvals': expenses_data,
            'total': approval_steps.total,
            'page': page,
            'pages': approval_steps.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@approval_bp.route('/<int:expense_id>/approve', methods=['POST'])
@jwt_required()
def approve_expense(expense_id):
    """
    Approve an expense
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        expense = Expense.query.get(expense_id)
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        # Check if expense is in company
        if expense.company_id != user.company_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json() or {}
        comments = data.get('comments', '')
        
        # Find the approval step for this user
        approval_step = ApprovalStep.query.filter_by(
            expense_id=expense_id,
            approver_id=user.id,
            status='pending'
        ).first()
        
        if not approval_step:
            return jsonify({'error': 'No pending approval found for this user'}), 400
        
        # Mark this step as approved
        approval_step.status = 'approved'
        approval_step.comments = comments
        approval_step.action_taken_at = datetime.utcnow()
        
        # Check if this is sequential approval
        all_steps = ApprovalStep.query.filter_by(expense_id=expense_id).order_by(ApprovalStep.step_order).all()
        
        # Get the approval rule
        rule = _get_applicable_rule(expense)
        
        if rule and rule.rule_type == 'sequential':
            # Sequential: move to next step
            next_step = ApprovalStep.query.filter_by(
                expense_id=expense_id,
                step_order=approval_step.step_order + 1
            ).first()
            
            if next_step:
                next_step.status = 'pending'
                expense.current_approval_step = next_step.step_order
            else:
                # No more steps, approve expense
                expense.status = 'approved'
        
        elif rule and rule.rule_type == 'conditional':
            # Conditional: check if conditions met
            if _check_conditional_approval(expense, rule):
                expense.status = 'approved'
        
        elif rule and rule.rule_type == 'hybrid':
            # Hybrid: check both sequential and conditional
            current_step_complete = all(
                step.status == 'approved' 
                for step in all_steps 
                if step.step_order <= approval_step.step_order
            )
            
            if current_step_complete:
                if _check_conditional_approval(expense, rule):
                    expense.status = 'approved'
                else:
                    # Move to next sequential step if exists
                    next_step = ApprovalStep.query.filter_by(
                        expense_id=expense_id,
                        step_order=approval_step.step_order + 1
                    ).first()
                    if next_step:
                        next_step.status = 'pending'
                    else:
                        expense.status = 'approved'
        else:
            # No rule or simple approval
            if all(step.status == 'approved' for step in all_steps):
                expense.status = 'approved'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Expense approved successfully',
            'expense': expense.to_dict(include_approvals=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@approval_bp.route('/<int:expense_id>/reject', methods=['POST'])
@jwt_required()
def reject_expense(expense_id):
    """
    Reject an expense
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        expense = Expense.query.get(expense_id)
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        if expense.company_id != user.company_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json() or {}
        comments = data.get('comments', '')
        
        if not comments:
            return jsonify({'error': 'Comments are required for rejection'}), 400
        
        # Find the approval step
        approval_step = ApprovalStep.query.filter_by(
            expense_id=expense_id,
            approver_id=user.id,
            status='pending'
        ).first()
        
        if not approval_step:
            return jsonify({'error': 'No pending approval found for this user'}), 400
        
        # Mark as rejected
        approval_step.status = 'rejected'
        approval_step.comments = comments
        approval_step.action_taken_at = datetime.utcnow()
        
        # Reject the entire expense
        expense.status = 'rejected'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Expense rejected successfully',
            'expense': expense.to_dict(include_approvals=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@approval_bp.route('/history', methods=['GET'])
@jwt_required()
def get_approval_history():
    """
    Get approval history for current user
    """
    try:
        user_id = get_jwt_identity()
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        approval_steps = ApprovalStep.query.filter_by(
            approver_id=user_id
        ).filter(
            ApprovalStep.status.in_(['approved', 'rejected'])
        ).order_by(ApprovalStep.action_taken_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        history = []
        for step in approval_steps.items:
            step_dict = step.to_dict()
            step_dict['expense'] = step.expense.to_dict()
            history.append(step_dict)
        
        return jsonify({
            'history': history,
            'total': approval_steps.total,
            'page': page,
            'pages': approval_steps.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _get_applicable_rule(expense):
    """
    Find applicable approval rule for expense
    """
    rules = ApprovalRule.query.filter_by(
        company_id=expense.company_id,
        is_active=True
    ).all()
    
    for rule in rules:
        if rule.min_amount and expense.amount < rule.min_amount:
            continue
        if rule.max_amount and expense.amount > rule.max_amount:
            continue
        if rule.category and rule.category != expense.category:
            continue
        return rule
    
    return None


def _check_conditional_approval(expense, rule):
    """
    Check if conditional approval conditions are met
    """
    if not rule.conditions:
        return False
    
    conditions = rule.conditions
    approved_steps = ApprovalStep.query.filter_by(
        expense_id=expense.id,
        status='approved'
    ).all()
    
    # Check percentage rule
    if 'percentage' in conditions:
        total_steps = ApprovalStep.query.filter_by(expense_id=expense.id).count()
        if total_steps > 0:
            approval_percentage = (len(approved_steps) / total_steps) * 100
            if approval_percentage >= conditions['percentage']:
                return True
    
    # Check specific approver rule
    if 'specific_approvers' in conditions:
        approved_ids = [step.approver_id for step in approved_steps]
        for approver_id in conditions['specific_approvers']:
            if approver_id in approved_ids:
                if conditions.get('operator') == 'OR':
                    return True
        
        # If AND operator (or no operator), all must approve
        if conditions.get('operator') != 'OR':
            if all(aid in approved_ids for aid in conditions['specific_approvers']):
                return True
    
    return False