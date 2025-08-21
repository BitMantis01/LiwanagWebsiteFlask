from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp
from models import User
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters'),
        Regexp(r'^[A-Za-z\s\-\']+$', message='First name can only contain letters, spaces, hyphens, and apostrophes')
    ])
    
    surname = StringField('Surname', validators=[
        DataRequired(message='Surname is required'),
        Length(min=2, max=50, message='Surname must be between 2 and 50 characters'),
        Regexp(r'^[A-Za-z\s\-\']+$', message='Surname can only contain letters, spaces, hyphens, and apostrophes')
    ])
    
    middle_initial = StringField('Middle Initial', validators=[
        Length(max=1, message='Middle initial must be a single character'),
        Regexp(r'^[A-Za-z]?$', message='Middle initial must be a letter')
    ])
    
    hospital_name = StringField('Hospital Name', validators=[
        DataRequired(message='Hospital name is required'),
        Length(min=3, max=100, message='Hospital name must be between 3 and 100 characters')
    ])
    
    hospital_room_no = StringField('Hospital Room No.', validators=[
        DataRequired(message='Hospital room number is required'),
        Length(min=1, max=20, message='Room number must be between 1 and 20 characters')
    ])
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters'),
        Regexp(r'^[A-Za-z0-9_.-]+$', message='Username can only contain letters, numbers, underscores, dots, and hyphens')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username is unique"""
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_password(self, password):
        """Validate password strength"""
        password_value = password.data
        errors = []
        
        # Check length
        if len(password_value) < 8:
            errors.append('Password must be at least 8 characters long')
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password_value):
            errors.append('Password must contain at least one uppercase letter')
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password_value):
            errors.append('Password must contain at least one lowercase letter')
        
        # Check for number
        if not re.search(r'\d', password_value):
            errors.append('Password must contain at least one number')
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password_value):
            errors.append('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')
        
        # Check for common patterns
        if password_value.lower() in ['password', '12345678', 'qwerty123', 'admin123']:
            errors.append('Password is too common. Please choose a more secure password')
        
        if errors:
            raise ValidationError(' '.join(errors))

class UpdateProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters'),
        Regexp(r'^[A-Za-z\s\-\']+$', message='First name can only contain letters, spaces, hyphens, and apostrophes')
    ])
    
    surname = StringField('Surname', validators=[
        DataRequired(message='Surname is required'),
        Length(min=2, max=50, message='Surname must be between 2 and 50 characters'),
        Regexp(r'^[A-Za-z\s\-\']+$', message='Surname can only contain letters, spaces, hyphens, and apostrophes')
    ])
    
    middle_initial = StringField('Middle Initial', validators=[
        Length(max=1, message='Middle initial must be a single character'),
        Regexp(r'^[A-Za-z]?$', message='Middle initial must be a letter')
    ])
    
    hospital_name = StringField('Hospital Name', validators=[
        DataRequired(message='Hospital name is required'),
        Length(min=3, max=100, message='Hospital name must be between 3 and 100 characters')
    ])
    
    hospital_room_no = StringField('Hospital Room No.', validators=[
        DataRequired(message='Hospital room number is required'),
        Length(min=1, max=20, message='Room number must be between 1 and 20 characters')
    ])
    
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, new_password):
        """Validate new password strength"""
        password_value = new_password.data
        errors = []
        
        # Check length
        if len(password_value) < 8:
            errors.append('Password must be at least 8 characters long')
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password_value):
            errors.append('Password must contain at least one uppercase letter')
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password_value):
            errors.append('Password must contain at least one lowercase letter')
        
        # Check for number
        if not re.search(r'\d', password_value):
            errors.append('Password must contain at least one number')
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password_value):
            errors.append('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')
        
        # Check for common patterns
        if password_value.lower() in ['password', '12345678', 'qwerty123', 'admin123']:
            errors.append('Password is too common. Please choose a more secure password')
        
        if errors:
            raise ValidationError(' '.join(errors))
