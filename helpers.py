import os
import uuid
from functools import wraps
from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename

def admin_required(f):
    """Decorator to check if the user is an admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def allow_file_type(filename):
    """Check if file type is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_verification_image(file_data):
    """Save uploaded verification image with unique filename"""
    # Generate a unique filename
    original_filename = secure_filename(file_data.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Save the file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file_data.save(file_path)
    
    return unique_filename
