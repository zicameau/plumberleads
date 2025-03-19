from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LeadSubmissionForm(FlaskForm):
    """Form for customers to submit new leads."""
    title = StringField('Problem Title', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Describe Your Problem', validators=[DataRequired(), Length(min=10, max=1000)])
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    customer_email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    customer_phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=50)])
    zip_code = StringField('ZIP Code', validators=[DataRequired(), Length(max=10)])
    
    service_type = SelectField('Service Type', validators=[DataRequired()], choices=[
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
    ])
    
    service_details = TextAreaField('Additional Details', validators=[Length(max=1000)])
    
    urgency = SelectField('How Urgent Is This?', validators=[DataRequired()], choices=[
        ('low', 'Low - Can wait a few days'),
        ('medium', 'Medium - Needs attention within 24 hours'),
        ('high', 'High - Needs immediate attention')
    ])
    
    submit = SubmitField('Submit Request')

class LeadFilterForm(FlaskForm):
    """Form for filtering leads."""
    service_type = SelectField('Service Type', choices=[
        ('', 'All Types'),
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
    ])
    
    zip_code = StringField('ZIP Code', validators=[Length(max=10)])
    
    sort = SelectField('Sort By', choices=[
        ('newest', 'Newest First'),
        ('price_high', 'Price: High to Low'),
        ('price_low', 'Price: Low to High'),
        ('urgency', 'Urgency')
    ])
    
    submit = SubmitField('Apply Filters') 