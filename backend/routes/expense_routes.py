from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, Expense, ApprovalStep, ApprovalRule
from datetime import datetime
from services.currency_service import CurrencyService

expense_bp = Blueprint('expense', __name__)
currency_service = CurrencyService()

@expense_bp.route('/', methods=['POST'])
@jwt_required()
def create_expense():
    """
    Employee submits a new expense
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'original_currency', 'category', 'expense_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse expense_date
        try:
            expense_date = datetime.strptime(data['expense_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Create expense
        expense = Expense(
            employee_id=user.id,
            company_id=user.company_id,
            amount=data['amount'],
            original_currency=data['original_currency'],
            category=data['category'],
            description=data.get('description'),
            expense_date=expense_date,
            receipt_url=data.get('receipt_url'),
            vendor_name=data.get('vendor_name'),
            status='pending'
        )
        
        db.session.add(expense)
        db.session.flush()  # Get expense ID
        
        # Create approval workflow
        _create_approval_workflow(expense, user)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Expense created successfully',
            'expense': expense.to_dict(include_approvals=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def _create_approval_workflow(expense, employee):
    """
    Create approval workflow based on rules
    """
    # Find applicable approval rule
    rules = ApprovalRule.query.filter_by(
        company_id=employee.company_id,
        is_active=True
    ).all()
    
    applicable_rule = None
    for rule in rules:
        # Check amount threshold
        if rule.min_amount and expense.amount < rule.min_amount:
            continue
        if rule.max_amount and expense.amount > rule.max_amount:
            continue
        
        # Check category
        if rule.category and rule.category != expense.category:
            continue
        
        applicable_rule = rule
        break
    
    if not applicable_rule:
        # Default workflow: just manager approval if manager exists
        if employee.manager and employee.is_manager_approver:
            step = ApprovalStep(
                expense_id=expense.id,
                approver_id=employee.manager.id,
                step_order=1,
                status='pending'
            )
            db.session.add(step)
        return
    
    # Create approval steps based on rule
    if applicable_rule.rule_type in ['sequential', 'hybrid']:
        # Sequential approval
        for idx, approver_id in enumerate(applicable_rule.approval_sequence or [], start=1):
            step = ApprovalStep(
                expense_id=expense.id,
                approver_id=approver_id,
                step_order=idx,
                status='pending' if idx == 1 else 'waiting'
            )
            db.session.add(step)
    
    elif applicable_rule.rule_type == 'conditional':
        # Conditional approval - create steps for all potential approvers
        conditions = applicable_rule.conditions or {}
        specific_approvers = conditions.get('specific_approvers', [])
        
        for idx, approver_id in enumerate(specific_approvers, start=1):
            step = ApprovalStep(
                expense_id=expense.id,
                approver_id=approver_id,
                step_order=idx,
                status='pending'
            )
            db.session.add(step)


@expense_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    """
    Get expenses - filtered by role
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Get query parameters
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query based on role
        if user.role == 'admin':
            # Admin sees all company expenses
            query = Expense.query.filter_by(company_id=user.company_id)
        elif user.role == 'manager':
            # Manager sees their expenses + subordinates' expenses
            subordinate_ids = [sub.id for sub in user.subordinates]
            query = Expense.query.filter(
                Expense.company_id == user.company_id,
                Expense.employee_id.in_(subordinate_ids + [user.id])
            )
        else:
            # Employee sees only their expenses
            query = Expense.query.filter_by(employee_id=user.id)
        
        # Filter by status
        if status:
            query = query.filter_by(status=status)
        
        # Paginate
        expenses = query.order_by(Expense.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'expenses': [exp.to_dict() for exp in expenses.items],
            'total': expenses.total,
            'page': page,
            'pages': expenses.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@expense_bp.route('/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    """
    Get single expense details
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        expense = Expense.query.get(expense_id)
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        # Check permissions
        if expense.company_id != user.company_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if user.role == 'employee' and expense.employee_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Convert amount to company currency if different
        converted_amount = None
        if expense.original_currency != user.company.currency:
            converted_amount = currency_service.convert(
                expense.amount,
                expense.original_currency,
                user.company.currency
            )
        
        expense_data = expense.to_dict(include_approvals=True)
        expense_data['converted_amount'] = converted_amount
        expense_data['company_currency'] = user.company.currency
        
        return jsonify({
            'expense': expense_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@expense_bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    """
    Update expense (only if pending and by owner)
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        expense = Expense.query.get(expense_id)
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        # Only owner can update
        if expense.employee_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Only pending expenses can be updated
        if expense.status != 'pending':
            return jsonify({'error': 'Cannot update non-pending expense'}), 400
        
        data = request.get_json()
        
        # Update fields
        if 'amount' in data:
            expense.amount = data['amount']
        if 'category' in data:
            expense.category = data['category']
        if 'description' in data:
            expense.description = data['description']
        if 'expense_date' in data:
            expense.expense_date = datetime.strptime(data['expense_date'], '%Y-%m-%d').date()
        if 'receipt_url' in data:
            expense.receipt_url = data['receipt_url']
        
        expense.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Expense updated successfully',
            'expense': expense.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """
    Delete expense (only if pending and by owner)
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        expense = Expense.query.get(expense_id)
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        # Only owner can delete
        if expense.employee_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Only pending expenses can be deleted
        if expense.status != 'pending':
            return jsonify({'error': 'Cannot delete non-pending expense'}), 400
        
        db.session.delete(expense)
        db.session.commit()
        
        return jsonify({
            'message': 'Expense deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@expense_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_expense_stats():
    """
    Get expense statistics
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Build query based on role
        if user.role == 'admin':
            query = Expense.query.filter_by(company_id=user.company_id)
        elif user.role == 'manager':
            subordinate_ids = [sub.id for sub in user.subordinates]
            query = Expense.query.filter(
                Expense.company_id == user.company_id,
                Expense.employee_id.in_(subordinate_ids + [user.id])
            )
        else:
            query = Expense.query.filter_by(employee_id=user.id)
        
        total = query.count()
        pending = query.filter_by(status='pending').count()
        approved = query.filter_by(status='approved').count()
        rejected = query.filter_by(status='rejected').count()
        
        total_amount = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.id.in_([e.id for e in query.all()])
        ).scalar() or 0
        
        return jsonify({
            'stats': {
                'total': total,
                'pending': pending,
                'approved': approved,
                'rejected': rejected,
                'total_amount': float(total_amount),
                'currency': user.company.currency
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500