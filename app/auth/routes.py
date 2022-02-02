from pydoc import render_doc
from app import db
from app.auth import bp
from app.auth.forms import RegistrationForm, LoginForm, ResetPasswordForm, ResetPasswordFormInput
from flask import render_template, flash, redirect, url_for, request
from app.models import User
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from datetime import datetime
from app.auth.email import send_password_reset_email

@bp.route('/login', methods =['GET', 'POST'])
def login():
    """ 
    This view function handles the login requests of the user.
    Before responding to the login request of the user, 
    This function checks if the user is not already logged in. If not,
    It displays a form that the user populates with their saved login information.
    It then redirects the user to the page they were trying to access, or to 
    the homepage by default.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.scheduleView'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.scheduleView')
        return redirect(next_page)
    return render_template('auth/login.html', title = 'Sign In', form=form)
@bp.route('/logout')
def logout():
    """ 
    This view function handles the logout requests of the user.
    It calls the built-in flask logout_user function
    """
    logout_user()
    return redirect(url_for('main.scheduleView'))
@bp.route('/register', methods = ['GET', 'POST'])
def register():
    """ 
    This view function handles the registration requests of the new users.
    Before doing that, it checks if the user is not already logged in. 
    If the user is not registered, the function adds their information to the database.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.scheduleView'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email= form.email.data, 
        first_name = form.first_name.data, last_name = form.last_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you have registered to use ScheduLit!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title = "Register", form=form)
@bp.route('auth/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """ 
    This view function allows the user reset password after requesting a reset.
    If the user is already logged in, a password reset is not allowed
    If the user is not logged in, the function provides a form to populate
    and updates the user's password in the database. The user is then redirect to 
    the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.scheduleView'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.scheduleView'))
    form = ResetPasswordFormInput()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
@bp.route('auth/resetPassword', methods=['GET', 'POST'])
def passwordReset():
    """ 
    This view function allows the user request password resets.
    If the user is already logged in, a password reset is not allowed
    If the user is not logged in, the function provides a form to populate
    and sends a reset link to the user's email.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.scheduleView'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/resetPassword.html',
                           title='Reset Password', form=form)