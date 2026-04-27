from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .modles import create_user, db, get_user_by_email

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = get_user_by_email(email) if email else None
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', category='success')
            return redirect(url_for('views.home'))

        flash('Invalid email or password.', category='error')
        return redirect(url_for('auth.login'))
   
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('application_id', None)
    session.pop('personal_info', None)
    session.pop('financial_info', None)
    session.pop('academic_info', None)
    session.pop('parental_info', None)
    session.pop('major_info', None)
    session.pop('additional_info', None)
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        first_name = request.form.get('firstName', '').strip()
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')

        if len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 2 characters.', category='error')
        elif get_user_by_email(email):
            flash('An account with that email already exists.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 9:
            flash('Password must be at least 9 characters.', category='error')
        else:
            user = create_user(email, first_name, password1)
            login_user(user)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
            
        return redirect(url_for('auth.sign_up'))

    return render_template('sign_up.html')


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('currentPassword', '')
        new_password = request.form.get('newPassword', '')
        confirm_password = request.form.get('confirmPassword', '')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', category='error')
        elif new_password != confirm_password:
            flash('New passwords do not match.', category='error')
        elif len(new_password) < 9:
            flash('New password must be at least 9 characters.', category='error')
        elif new_password == current_password:
            flash('New password must be different from the current password.', category='error')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully.', category='success')
            return redirect(url_for('views.home'))

        return redirect(url_for('auth.change_password'))

    return render_template('change_password.html')
