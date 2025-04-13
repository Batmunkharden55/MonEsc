import os
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import app, db
from models import User, Profile, VerificationImage
from forms import LoginForm, RegistrationForm, ProfileForm, AdminLoginForm, VerificationForm
from helpers import admin_required, save_verification_image, allow_file_type

# Client routes
@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/escorts')
def escort_list():
    """Show list of verified escorts with filters"""
    age_filter = request.args.get('age', type=int)
    weight_filter = request.args.get('weight', type=int)
    location_filter = request.args.get('location', '')
    
    # Base query - only verified profiles
    query = Profile.query.filter_by(is_verified=True)
    
    # Apply filters if provided
    if age_filter:
        query = query.filter_by(age=age_filter)
    if weight_filter:
        query = query.filter_by(weight=weight_filter)
    if location_filter:
        query = query.filter(Profile.location.ilike(f'%{location_filter}%'))
    
    # Get the filtered escorts
    escorts = query.all()
    
    # Get unique locations for filter dropdown
    locations = db.session.query(Profile.location).filter_by(is_verified=True).distinct().all()
    locations = [loc[0] for loc in locations]
    
    return render_template('escort_list.html', 
                          escorts=escorts, 
                          locations=locations,
                          age_filter=age_filter,
                          weight_filter=weight_filter,
                          location_filter=location_filter)

@app.route('/escorts/<int:profile_id>')
def escort_detail(profile_id):
    """Show detailed information about an escort"""
    profile = Profile.query.get_or_404(profile_id)
    
    # Only allow viewing verified profiles
    if not profile.is_verified:
        flash('This profile is not available.', 'danger')
        return redirect(url_for('escort_list'))
    
    return render_template('escort_detail.html', profile=profile)

# Escort authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route for escorts"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('profile'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route for escorts"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken. Please choose another.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            password_hash=hashed_password,
            role='escort'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please create your profile.', 'success')
        login_user(new_user)
        return redirect(url_for('profile'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Escort profile routes
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Escort profile creation/edit page"""
    # Check if user is an escort
    if current_user.role != 'escort':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Get existing profile or prepare for a new one
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    form = ProfileForm(obj=profile)
    
    if form.validate_on_submit():
        if profile:
            # Update existing profile
            profile.nickname = form.nickname.data
            profile.phone_number = form.phone_number.data
            profile.age = form.age.data
            profile.weight = form.weight.data
            profile.height = form.height.data
            profile.location = form.location.data
            
            # If profile was rejected, allow resubmission
            if profile.is_rejected:
                profile.is_rejected = False
                profile.verification_note = None
            
            # Set to not verified when updating profile
            if profile.is_verified:
                profile.is_verified = False
                flash('Your profile has been updated and will need to be verified again.', 'warning')
        else:
            # Create new profile
            profile = Profile(
                user_id=current_user.id,
                nickname=form.nickname.data,
                phone_number=form.phone_number.data,
                age=form.age.data,
                weight=form.weight.data,
                height=form.height.data,
                location=form.location.data
            )
            db.session.add(profile)
            db.session.flush()  # Get profile ID without committing
        
        # Handle verification image upload
        if form.verification_image.data:
            # Save the verification image
            filename = save_verification_image(form.verification_image.data)
            
            # Create verification image record
            verification_image = VerificationImage(
                profile_id=profile.id,
                filename=filename
            )
            db.session.add(verification_image)
        
        db.session.commit()
        flash('Your profile has been saved and is pending verification.', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form, profile=profile)

# Admin routes
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    # If already logged in as admin, redirect to dashboard
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        # Check admin code (215899)
        if form.admin_code.data == "215899":
            # Check if admin user already exists
            admin = User.query.filter_by(role='admin').first()
            
            # Create admin user if doesn't exist
            if not admin:
                admin = User(
                    username=f"admin_{uuid.uuid4().hex[:8]}",
                    password_hash=generate_password_hash("not_used_for_admin"),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
            
            login_user(admin)
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin code.', 'danger')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard to see pending profiles"""
    # Get profiles that need verification (not verified and not rejected)
    pending_profiles = Profile.query.filter_by(is_verified=False, is_rejected=False).all()
    return render_template('admin_dashboard.html', profiles=pending_profiles)

@app.route('/admin/verify/<int:profile_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_verify(profile_id):
    """Admin verification page for a specific profile"""
    profile = Profile.query.get_or_404(profile_id)
    form = VerificationForm()
    
    if form.validate_on_submit():
        if 'approve' in request.form:
            profile.is_verified = True
            profile.is_rejected = False
            flash(f'Profile for {profile.nickname} has been approved.', 'success')
        elif 'reject' in request.form:
            profile.is_verified = False
            profile.is_rejected = True
            profile.verification_note = form.verification_note.data
            flash(f'Profile for {profile.nickname} has been rejected.', 'warning')
        
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    # Get the most recent verification image
    verification_image = VerificationImage.query.filter_by(profile_id=profile.id).order_by(VerificationImage.upload_date.desc()).first()
    
    return render_template('admin_verify.html', profile=profile, form=form, verification_image=verification_image)
