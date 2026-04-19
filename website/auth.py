from flask import Blueprint, render_template, request, flash, redirect, url_for

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Dummy success condition: if email and password are provided
        if email and password:
            flash('Login successful!', category='success')
            return redirect(url_for('views.home'))
        else:
            flash('Invalid email or password.', category='error')
            return redirect(url_for('auth.login'))
   
    return render_template('login.html')

@auth.route('/logout')
def logout():
    return render_template('logout.html')  

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 2 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 9:
            flash('Password must be at least 9 characters.', category='error')
        else:
            flash('Account created!', category='success')
            return redirect(url_for('auth.login'))  # Redirect to login after successful sign-up
            
        return redirect(url_for('auth.sign_up'))  # Redirect to show error messages

    return render_template('sign_up.html')
