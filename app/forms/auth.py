from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectMultipleField, FileField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange

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
    latitude = FloatField('Latitude', validators=[DataRequired(), NumberRange(-90, 90)])
    longitude = FloatField('Longitude', validators=[DataRequired(), NumberRange(-180, 180)])
    service_radius = IntegerField('Service Radius (miles)', validators=[DataRequired(), NumberRange(1, 100)], default=25)
    
    # Service areas and types
    service_areas = SelectMultipleField('Service Areas', choices=[
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
    ], validators=[DataRequired()])
    
    service_types = SelectMultipleField('Service Types', choices=[
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
    ], validators=[DataRequired()])
    
    submit = SubmitField('Register') 