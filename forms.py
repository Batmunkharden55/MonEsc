from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError

class LoginForm(FlaskForm):
    """Form for escort login"""
    username = StringField('Хэрэглэгчийн нэр', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Нууц үг', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Нэвтрэх')

class RegistrationForm(FlaskForm):
    """Form for escort registration"""
    username = StringField('Хэрэглэгчийн нэр', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Нууц үг', validators=[
        DataRequired(), 
        Length(min=6, message="Нууц үг дор хаяж 6 тэмдэгт байх ёстой")
    ])
    confirm_password = PasswordField('Нууц үг баталгаажуулах', validators=[
        DataRequired(), 
        EqualTo('password', message='Нууц үгнүүд таарахгүй байна')
    ])
    submit = SubmitField('Бүртгүүлэх')

class ProfileForm(FlaskForm):
    """Form for escort profile creation/editing"""
    nickname = StringField('Нэр', validators=[DataRequired(), Length(min=2, max=50)])
    phone_number = StringField('Утасны дугаар', validators=[DataRequired(), Length(min=8, max=20)])
    age = IntegerField('Нас', validators=[
        DataRequired(),
        NumberRange(min=18, max=99, message="Нас 18-99 хооронд байх ёстой")
    ])
    weight = IntegerField('Жин (кг)', validators=[
        DataRequired(),
        NumberRange(min=30, max=200, message="Жин 30-200 кг хооронд байх ёстой")
    ])
    height = IntegerField('Өндөр (см)', validators=[
        DataRequired(),
        NumberRange(min=120, max=220, message="Өндөр 120-220 см хооронд байх ёстой")
    ])
    location = StringField('Байршил', validators=[DataRequired(), Length(max=100)])
    verification_image = FileField('Баталгаажуулах зураг', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Зөвхөн зураг!')
    ])
    submit = SubmitField('Профайл хадгалах')

class AdminLoginForm(FlaskForm):
    """Form for admin login"""
    admin_code = PasswordField('Админ код', validators=[DataRequired()])
    submit = SubmitField('Нэвтрэх')

class VerificationForm(FlaskForm):
    """Form for admin verification of profiles"""
    verification_note = TextAreaField('Тэмдэглэл (Заавал биш)')
    approve = SubmitField('Зөвшөөрөх')
    reject = SubmitField('Татгалзах')
