from flask import request, jsonify, current_app, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.models.user import User
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
import json

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is active
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    # Populate service area and service type choices
    # These would typically come from a database or configuration
    form.service_areas.choices = [
        ('New York, NY', 'New York, NY'),
        ('Los Angeles, CA', 'Los Angeles, CA'),
        ('Chicago, IL', 'Chicago, IL'),
        ('Houston, TX', 'Houston, TX'),
        ('Phoenix, AZ', 'Phoenix, AZ'),
        ('Philadelphia, PA', 'Philadelphia, PA'),
        ('San Antonio, TX', 'San Antonio, TX'),
        ('San Diego, CA', 'San Diego, CA'),
        ('Dallas, TX', 'Dallas, TX'),
        ('San Jose, CA', 'San Jose, CA')
    ]
    
    form.service_types.choices = [
        ('Residential Plumbing', 'Residential Plumbing'),
        ('Commercial Plumbing', 'Commercial Plumbing'),
        ('Emergency Repairs', 'Emergency Repairs'),
        ('Water Heater Installation', 'Water Heater Installation'),
        ('Pipe Repair', 'Pipe Repair'),
        ('Drain Cleaning', 'Drain Cleaning'),
        ('Sewer Line Repair', 'Sewer Line Repair'),
        ('Fixture Installation', 'Fixture Installation'),
        ('Gas Line Services', 'Gas Line Services'),
        ('Water Treatment', 'Water Treatment')
    ]
    
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            full_name=form.full_name.data,
            company_name=form.company_name.data,
            phone=form.phone.data,
            is_active=True,
            is_admin=False,
            is_verified=False  # Users start unverified
        )
        user.set_password(form.password.data)
        
        # Set service areas and types
        user.service_areas = json.dumps(form.service_areas.data)
        user.service_types = json.dumps(form.service_types.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered plumber! Please check your email to verify your account.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # In a real application, send an email with a password reset link
            # For this implementation, we'll just flash a message
            flash('Check your email for instructions to reset your password', 'success')
        else:
            flash('Check your email for instructions to reset your password', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # In a real application, verify the token and get the user
    # user = User.verify_reset_password_token(token)
    # if not user:
    #     return redirect(url_for('index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # In a real application, set the new password for the user
        # user.set_password(form.password.data)
        # db.session.commit()
        
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

# API routes for mobile/SPA clients

@bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email'].lower()).first()
    
    if user is None or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    login_user(user)
    
    return jsonify({
        'user': user.to_dict(),
        'message': 'Login successful'
    })

@bp.route('/api/logout', methods=['POST'])
def api_logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})

@bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    
    required_fields = ['email', 'password', 'full_name', 'company_name', 'phone', 
                      'service_areas', 'service_types']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'error': 'Email address already in use'}), 400
    
    user = User(
        email=data['email'].lower(),
        full_name=data['full_name'],
        company_name=data['company_name'],
        phone=data['phone'],
        is_active=True,
        is_admin=False,
        is_verified=False
    )
    user.set_password(data['password'])
    
    # Set service areas and types
    user.service_areas = json.dumps(data['service_areas'])
    user.service_types = json.dumps(data['service_types'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@bp.route('/api/me', methods=['GET'])
@login_required
def api_me():
    return jsonify(current_user.to_dict()) 