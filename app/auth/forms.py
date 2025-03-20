from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField, TextAreaField, IntegerField, HiddenField, FileField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from app.models.user import User
from werkzeug.utils import secure_filename
import os

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    business_description = TextAreaField('Business Description', validators=[DataRequired(), Length(min=50, max=500)])
    license_number = StringField('License Number', validators=[DataRequired(), Length(min=5, max=50)])
    has_insurance = BooleanField('I have insurance')
    profile_image = FileField('Profile Image', validators=[Optional()])
    
    # Address fields
    address = StringField('Business Address', validators=[DataRequired(), Length(max=255)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=2)])
    zip_code = StringField('ZIP Code', validators=[DataRequired(), Length(min=5, max=10)])
    latitude = HiddenField('Latitude', validators=[Optional()])
    longitude = HiddenField('Longitude', validators=[Optional()])
    service_radius = IntegerField('Service Radius (miles)', validators=[DataRequired(), NumberRange(1, 100)], default=25)
    
    # Service areas and types
    service_areas = SelectMultipleField('Service Areas', choices=[
        ('New York', 'New York'),
        ('Los Angeles', 'Los Angeles'),
        ('Chicago', 'Chicago'),
        ('Houston', 'Houston'),
        ('Phoenix', 'Phoenix'),
        ('Philadelphia', 'Philadelphia'),
        ('San Antonio', 'San Antonio'),
        ('San Diego', 'San Diego'),
        ('Dallas', 'Dallas'),
        ('San Jose', 'San Jose')
    ], validators=[DataRequired()])
    
    service_types = SelectMultipleField('Service Types', choices=[
        ('Emergency Repair', 'Emergency Repair'),
        ('Leak Detection', 'Leak Detection'),
        ('Drain Cleaning', 'Drain Cleaning'),
        ('Pipe Installation', 'Pipe Installation'),
        ('Water Heater Service', 'Water Heater Service'),
        ('Fixture Installation', 'Fixture Installation'),
        ('Sewer Repair', 'Sewer Repair'),
        ('Backflow Testing', 'Backflow Testing'),
        ('Water Line Repair', 'Water Line Repair'),
        ('Commercial Plumbing', 'Commercial Plumbing')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email address.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password') 