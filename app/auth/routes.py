from flask import render_template, redirect, url_for, flash, request, session
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models.user import User
from app.services.supabase import get_supabase_client
import json
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os
from werkzeug.utils import secure_filename
from flask import current_app

logger = logging.getLogger(__name__)

def geocode_address(address, city, state, zip_code):
    """Convert address to coordinates using geopy."""
    try:
        geolocator = Nominatim(user_agent="plumberleads")
        full_address = f"{address}, {city}, {state} {zip_code}"
        location = geolocator.geocode(full_address)
        if location:
            return location.latitude, location.longitude
        return None, None
    except GeocoderTimedOut:
        logger.error("Geocoding timed out")
        return None, None
    except Exception as e:
        logger.error(f"Geocoding error: {str(e)}")
        return None, None

def save_profile_image(file):
    """Save a profile image and return the filename."""
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Ensure the upload folder exists
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
        
        # Save the file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            supabase = get_supabase_client()
            response = supabase.auth.sign_in_with_password({
                'email': form.email.data.lower(),
                'password': form.password.data
            })
            
            if response.user:
                # Get user profile from our database
                user = User.query.filter_by(email=form.email.data.lower()).first()
                if user:
                    session['user'] = {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_admin': user.is_admin
                    }
                    
                    next_page = request.args.get('next')
                    if not next_page or not next_page.startswith('/'):
                        next_page = url_for('index')
                    return redirect(next_page)
                else:
                    logger.error(f"User profile not found for email: {form.email.data.lower()}")
                    flash('User profile not found. Please try registering again.', 'danger')
            else:
                flash('Invalid email or password', 'danger')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login', 'danger')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
    
    session.clear()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user'):
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            logger.info("Starting registration process")
            # First create the user in Supabase
            supabase = get_supabase_client()
            auth_response = supabase.auth.sign_up({
                'email': form.email.data.lower(),
                'password': form.password.data
            })
            
            if not auth_response.user:
                logger.error("Failed to create Supabase user")
                flash('Failed to create user account', 'danger')
                return redirect(url_for('auth.register'))
            
            logger.info(f"Successfully created Supabase user: {auth_response.user.id}")
            
            # Handle profile image upload
            profile_image = None
            if form.profile_image.data:
                try:
                    profile_image = save_profile_image(form.profile_image.data)
                    logger.info(f"Successfully uploaded profile image: {profile_image}")
                except Exception as img_error:
                    logger.error(f"Failed to upload profile image: {str(img_error)}")
                    # Continue with registration even if image upload fails
            
            # Get coordinates if not provided
            latitude = form.latitude.data
            longitude = form.longitude.data
            
            if not latitude or not longitude:
                logger.info("No coordinates provided, attempting to geocode address")
                latitude, longitude = geocode_address(
                    form.address.data,
                    form.city.data,
                    form.state.data,
                    form.zip_code.data
                )
                if latitude and longitude:
                    logger.info(f"Successfully geocoded address: {latitude}, {longitude}")
                else:
                    logger.warning("Failed to geocode address")
            
            # Create user profile in our database
            try:
                user = User(
                    id=auth_response.user.id,  # Use Supabase user ID
                    full_name=form.full_name.data,
                    email=form.email.data.lower(),
                    company_name=form.company_name.data,
                    phone=form.phone.data,
                    business_description=form.business_description.data,
                    license_number=form.license_number.data,
                    has_insurance=form.has_insurance.data,
                    profile_image=profile_image,
                    # Address fields
                    address=form.address.data,
                    city=form.city.data,
                    state=form.state.data,
                    zip_code=form.zip_code.data,
                    latitude=latitude,
                    longitude=longitude,
                    service_radius=form.service_radius.data,
                    # Service areas and types
                    service_areas=json.dumps(form.service_areas.data),
                    service_types=json.dumps(form.service_types.data),
                    is_active=True,
                    is_admin=False,
                    is_verified=False
                )
                
                logger.info("Created User object, attempting to add to database session")
                # Add user to database session
                db.session.add(user)
                # Commit the transaction
                db.session.commit()
                logger.info("Successfully committed user to database")
                
                # Verify the user was created in our database
                created_user = User.query.filter_by(email=form.email.data.lower()).first()
                if not created_user:
                    logger.error("User was not found in database after creation")
                    raise Exception("User profile was not created in database")
                
                logger.info("Registration completed successfully")
                flash('Registration successful! Please check your email to verify your account.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as db_error:
                logger.error(f"Database error during registration: {str(db_error)}")
                # Rollback the transaction in case of error
                db.session.rollback()
                # If database operation fails, delete the Supabase account
                try:
                    logger.info("Attempting to delete Supabase user after database error")
                    supabase.auth.admin.delete_user(auth_response.user.id)
                except Exception as delete_error:
                    logger.error(f"Failed to delete Supabase user after database error: {str(delete_error)}")
                flash('Failed to create user profile. Please try again.', 'danger')
                return redirect(url_for('auth.register'))
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            # If there was an error, try to delete the Supabase account
            try:
                if 'auth_response' in locals() and auth_response.user:
                    logger.info("Attempting to delete Supabase user after registration error")
                    supabase.auth.admin.delete_user(auth_response.user.id)
            except Exception as delete_error:
                logger.error(f"Failed to delete Supabase user after registration error: {str(delete_error)}")
            flash('An error occurred during registration', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if session.get('user'):
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        try:
            supabase = get_supabase_client()
            response = supabase.auth.reset_password_for_email(form.email.data.lower())
            
            if response:
                flash('Check your email for instructions to reset your password', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('Email address not found', 'warning')
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            flash('An error occurred while processing your request', 'danger')
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if session.get('user'):
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            supabase = get_supabase_client()
            response = supabase.auth.update_user({
                'password': form.password.data
            })
            
            if response:
                flash('Your password has been reset.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Failed to reset password', 'danger')
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            flash('An error occurred while resetting your password', 'danger')
    
    return render_template('auth/reset_password.html', form=form) 