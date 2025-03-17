# app/routes/auth.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, session, current_app
from app.services.auth_service import signup, login, logout, reset_password, get_current_user
from flask_mail import Message, Mail
import os
from app import mail
import logging
from app.models.plumber import Plumber

# Get the auth logger
logger = logging.getLogger('auth')

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

PLUMBING_SERVICES = [
    {'id': 'emergency', 'name': 'Emergency Plumbing'},
    {'id': 'leak', 'name': 'Leak Detection & Repair'},
    {'id': 'drain', 'name': 'Drain Cleaning'},
    {'id': 'toilet', 'name': 'Toilet Repair/Installation'},
    {'id': 'faucet', 'name': 'Faucet Repair/Installation'},
    {'id': 'sink', 'name': 'Sink Repair/Installation'},
    {'id': 'disposal', 'name': 'Garbage Disposal Repair/Installation'},
    {'id': 'water_heater', 'name': 'Water Heater Services'},
    {'id': 'sewer', 'name': 'Sewer Line Services'},
    {'id': 'repiping', 'name': 'Repiping Services'},
    {'id': 'gas_line', 'name': 'Gas Line Installation/Repair'},
    {'id': 'backflow', 'name': 'Backflow Prevention'},
    {'id': 'waterproofing', 'name': 'Basement Waterproofing'},
    {'id': 'sump_pump', 'name': 'Sump Pump Services'},
    {'id': 'commercial', 'name': 'Commercial Plumbing'},
    {'id': 'inspection', 'name': 'Plumbing Inspection'},
    {'id': 'maintenance', 'name': 'Preventative Maintenance'},
    {'id': 'renovation', 'name': 'Bathroom/Kitchen Renovation Plumbing'},
    {'id': 'other', 'name': 'Other Plumbing Services'}
]

@auth_bp.route('/register/plumber', methods=['GET', 'POST'])
def register_plumber():
    """Registration page for plumbers."""
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Separate plumber profile data from auth data
        plumber_data = {
            'company_name': request.form.get('company_name'),
            'contact_name': request.form.get('contact_name'),
            'email': email,  # Include email in profile
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip_code': request.form.get('zip_code'),
            'service_radius': int(request.form.get('service_radius', 25)),
            'services_offered': request.form.getlist('services_offered'),
            'license_number': request.form.get('license_number'),
            'is_insured': request.form.get('is_insured') == 'yes'
        }
        
        # Basic validation
        if not all([email, password, confirm_password, plumber_data['company_name']]):
            flash('All required fields must be filled out', 'error')
            return render_template('auth/register_plumber.html', 
                                form_data=plumber_data,
                                services=PLUMBING_SERVICES)
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register_plumber.html', 
                                form_data=plumber_data,
                                services=PLUMBING_SERVICES)

        # Geocode the address if provided
        if all([plumber_data['address'], plumber_data['city'], 
               plumber_data['state'], plumber_data['zip_code']]):
            from app.services.lead_service import geocode_address
            try:
                latitude, longitude = geocode_address(
                    plumber_data['address'],
                    plumber_data['city'],
                    plumber_data['state'],
                    plumber_data['zip_code']
                )
                plumber_data['latitude'] = latitude
                plumber_data['longitude'] = longitude
            except Exception as e:
                flash('Could not validate your address. Please check and try again.', 'error')
                return render_template('auth/register_plumber.html', 
                                    form_data=plumber_data,
                                    services=PLUMBING_SERVICES)

        # Create user with plumber role
        user_metadata = {
            'role': 'plumber',
            'company_name': plumber_data['company_name']
        }
        
        user = signup(email, password, user_metadata)
        
        if user:
            # Create plumber profile
            plumber_data['user_id'] = user.id
            plumber = Plumber.create(plumber_data)
            
            if not plumber:
                # If profile creation fails, we should handle this case
                # Ideally with a cleanup of the created user
                flash('Registration successful but profile creation failed. Please contact support.', 'warning')
            
            # Store user info for redirection after email confirmation
            session['registered_email'] = email
            session['registered_role'] = 'plumber'
            
            logger.info(f"Plumber registration successful for {email}")
            flash('Registration successful! Please check your email to confirm your account.', 'success')
            return redirect(url_for('auth.registration_success'))
        else:
            logger.warning(f"Plumber registration failed for {email}")
            flash('Registration failed. This email may already be registered.', 'error')
            return render_template('auth/register_plumber.html', 
                                form_data=plumber_data,
                                services=PLUMBING_SERVICES)
    
    # GET request - show registration form
    return render_template('auth/register_plumber.html', 
                         services=PLUMBING_SERVICES)

@auth_bp.route('/registration-success')
def registration_success():
    """Registration success page."""
    email = session.pop('registered_email', None)
    role = session.pop('registered_role', None)
    
    if not email or not role:
        return redirect(url_for('home.index'))
    
    return render_template('auth/registration_success.html', 
                         email=email,
                         role=role)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_route():
    """Login page."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = login(email, password)
        if user:
            flash('Login successful!', 'success')
            return redirect(url_for('home.index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout_route():
    """Logout route."""
    if logout():
        flash('You have been logged out.', 'success')
    return redirect(url_for('home.index'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_route():
    """Password reset request page."""
    if request.method == 'POST':
        email = request.form.get('email')
        if reset_password(email):
            flash('Password reset instructions have been sent to your email.', 'success')
        else:
            flash('Failed to send password reset instructions. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
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