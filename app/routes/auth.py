# app/routes/auth.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, session, current_app
from app.services.auth_service import signup, login, logout, reset_password_request
from flask_mail import Message, Mail
import os
from app import mail
import logging

# Get the auth logger
logger = logging.getLogger('auth')

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register/plumber', methods=['GET', 'POST'])
def register_plumber():
    """Registration page for plumbers."""
    if request.method == 'POST':
        logger.info(f"Plumber registration form submitted for {request.form.get('email')}")
        
        # Validate form data
        if request.form.get('password') != request.form.get('confirm_password'):
            flash('Passwords do not match', 'error')
            return render_template('auth/register_plumber.html')
            
        # Prepare user metadata
        metadata = {
            'role': 'plumber',
            'company_name': request.form.get('company_name'),
            'contact_name': request.form.get('contact_name'),
            'phone': request.form.get('phone')
        }
        
        logger.info(f"Attempting to create plumber account for {request.form.get('email')}")
        auth_response = signup(
            request.form.get('email'),
            request.form.get('password'),
            metadata=metadata
        )
        
        if auth_response and auth_response.user:
            flash('Registration successful! Please check your email to confirm your account.', 'success')
            return redirect(url_for('auth.login'))
            
        flash('Registration failed. Please try again.', 'error')
        logger.warning(f"Plumber registration failed for {request.form.get('email')}")
        
    # GET request - show registration form
    logger.info("Plumber registration form requested")
    return render_template('auth/register_plumber.html')

@auth_bp.route('/register/success', methods=['GET'])
def registration_success():
    """Registration success page."""
    registered_email = session.get('registered_email')
    registered_role = session.get('registered_role')
    
    # Clear session data
    session.pop('registered_email', None)
    session.pop('registered_role', None)
    
    return render_template('auth/registration_success.html', 
                         email=registered_email,
                         role=registered_role)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_route():
    """Login page."""
    # Check if already logged in
    if 'token' in session:
        # Get role from metadata if available
        role = session.get('role')
        user_id = session.get('user_id')
        
        logger.info(f"Already logged in user {user_id} with role {role} attempting to access login page")
        
        if role == 'plumber':
            return redirect(url_for('plumber.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('customer.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        logger.info(f"Login attempt for {email}")
        auth_response = login(email, password)
        
        if auth_response and auth_response.user:
            flash('Logged in successfully!', 'success')
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(url_for('main.index'))
            
        flash('Invalid email or password', 'error')
        logger.warning(f"Login failed for {email}")
        
    # GET request - show login form
    logger.info("Login form requested")
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET'])
def logout_route():
    """Logout and redirect to home page."""
    user_email = session.get('user', {}).get('email')
    logger.info(f"Logout requested for user {user_email}")
    
    logout()
    flash('You have been logged out successfully', 'success')
    logger.info(f"User {user_email} logged out successfully")
    
    return redirect(url_for('main.index'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset request page."""
    if request.method == 'POST':
        email = request.form.get('email')
        logger.info(f"Password reset requested for {email}")
        
        if reset_password_request(email):
            flash('Password reset instructions have been sent to your email', 'success')
            return redirect(url_for('auth.login'))
            
        flash('Error sending password reset email. Please try again.', 'error')
        
    # GET request - show reset password form
    return render_template('auth/reset_password.html')

@auth_bp.route('/confirm', methods=['GET'])
def confirm_email():
    """Email confirmation handler."""
    # This route handles the redirect from Supabase email confirmation
    # The token is handled by Supabase automatically
    
    flash('Your email has been confirmed. You can now log in.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login."""
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        # Attempt login
        result = login(data['email'], data['password'])
        
        if result and result.user:
            # Return token and basic user info
            return jsonify({
                'success': True,
                'token': result.session.access_token,
                'user': {
                    'id': result.user.id,
                    'email': result.user.email,
                    'role': result.user.user_metadata.get('role')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/api/register/plumber', methods=['POST'])
def api_register_plumber():
    """API endpoint for plumber registration."""
    try:
        # Get JSON data
        data = request.get_json()
        
        required_fields = ['email', 'password', 'company_name']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Create user with plumber role
        user_metadata = {
            'role': 'plumber',
            'company_name': data['company_name']
        }
        
        user = signup(data['email'], data['password'], user_metadata)
        
        if user:
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please check your email to confirm your account.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Registration failed. This email may already be registered.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500