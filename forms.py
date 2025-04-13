from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError

class LoginForm(FlaskForm):
    """Form for escort login"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Form for escort registration"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    """Form for escort profile creation/editing"""
    nickname = StringField('Nickname', validators=[DataRequired(), Length(min=2, max=50)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=8, max=20)])
    age = IntegerField('Age', validators=[
        DataRequired(),
        NumberRange(min=18, max=99, message="Age must be between 18 and 99")
    ])
    weight = IntegerField('Weight (kg)', validators=[
        DataRequired(),
        NumberRange(min=30, max=200, message="Weight must be between 30 and 200 kg")
    ])
    height = IntegerField('Height (cm)', validators=[
        DataRequired(),
        NumberRange(min=120, max=220, message="Height must be between 120 and 220 cm")
    ])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    verification_image = FileField('Verification Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Save Profile')

class AdminLoginForm(FlaskForm):
    """Form for admin login"""
    admin_code = PasswordField('Admin Code', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class VerificationForm(FlaskForm):
    """Form for admin verification of profiles"""
    verification_note = TextAreaField('Note (Optional)')
    approve = SubmitField('Approve')
    reject = SubmitField('Reject')
