# app/routes/auth.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, session, current_app
from app.services.auth_service import signup, login as auth_login, logout, reset_password_request
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
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        company_name = request.form.get('company_name')
        
        logger.info(f"Plumber registration form submitted for {email}")
        
        if not all([email, password, confirm_password, company_name]):
            logger.warning(f"Incomplete plumber registration form for {email}")
            flash('All fields are required', 'error')
            return render_template('auth/register_plumber.html')
            
        if password != confirm_password:
            logger.warning(f"Password mismatch in plumber registration for {email}")
            flash('Passwords do not match', 'error')
            return render_template('auth/register_plumber.html', form_data=request.form)
        
        # Create user with plumber role
        user_metadata = {
            'role': 'plumber',
            'company_name': company_name
        }
        
        logger.info(f"Attempting to create plumber account for {email}")
        user = signup(email, password, user_metadata)
        
        if user:
            # Store user info for redirection after email confirmation
            session['registered_email'] = email
            session['registered_role'] = 'plumber'
            
            logger.info(f"Plumber registration successful for {email}")
            flash('Registration successful! Please check your email to confirm your account.', 'success')
            return redirect(url_for('auth.registration_success'))
        else:
            logger.warning(f"Plumber registration failed for {email}")
            flash('Registration failed. This email may already be registered.', 'error')
            return render_template('auth/register_plumber.html', form_data=request.form)
    
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
def login():
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
        
        if not email or not password:
            logger.warning(f"Login attempt with missing credentials")
            flash('Email and password are required', 'error')
            return render_template('auth/login.html', email=email)
        
        # Attempt login
        logger.info(f"Attempting login for {email}")
        result = auth_login(email, password)
        
        if result and result.get('session') and result.get('user'):
            # Store token and basic user info in session
            session['token'] = result['session'].access_token
            session['user_id'] = result['user'].id
            
            # Store role for redirects
            user_metadata = result['user'].user_metadata or {}
            role = user_metadata.get('role')
            session['role'] = role
            
            logger.info(f"Login successful for {email} with role {role}")
            
            # Redirect based on role
            if role == 'plumber':
                return redirect(url_for('plumber.dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('customer.index'))
        else:
            logger.warning(f"Login failed for {email}")
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html', email=email)
    
    # GET request - show login form
    logger.info("Login form requested")
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET'])
def logout_route():
    """Logout and redirect to home page."""
    user_id = session.get('user_id')
    logger.info(f"Logout requested for user {user_id}")
    
    if 'token' in session:
        token = session['token']
        logout(token)
    
    # Clear session
    session.clear()
    
    logger.info(f"User {user_id} logged out successfully")
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home.index'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset request page."""
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        
        if not email:
            flash('Email is required', 'error')
            return render_template('auth/reset_password.html')
        
        # Send password reset email
        reset_sent = reset_password_request(email)
        
        if reset_sent:
            flash('Password reset instructions have been sent to your email.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Failed to send password reset email. Please try again.', 'error')
            return render_template('auth/reset_password.html', email=email)
    
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
        result = auth_login(data['email'], data['password'])
        
        if result and result.get('session') and result.get('user'):
            # Return token and basic user info
            return jsonify({
                'success': True,
                'token': result['session'].access_token,
                'user': {
                    'id': result['user'].id,
                    'email': result['user'].email,
                    'role': result['user'].user_metadata.get('role')
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