from flask import Blueprint, render_template, redirect, flash, url_for, current_app
from app import db
from app.forms import RegisterForm, LoginForm
from flask_login import login_user, login_required, logout_user
from datetime import datetime
from app.models.user import User
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Safety: make sure tables exist (prevents "no such table" during dev)
        try:
            db.create_all()
        except Exception:
            logging.exception("Failed to ensure DB tables exist before registration")

        try:
            user = User(
                username=form.username.data,  # type: str
                fullname=form.fullname.data,  # type: str
                qualification=form.qualification.data,  # type: str
                dob=datetime.strptime(str(form.dob.data), '%Y-%m-%d').date(),  # convert to date
                is_admin=False,  # type: bool
                avatar='person-circle'  # default avatar
            )
        except Exception:
            user = User(
                    username=form.username.data,
                    fullname=form.fullname.data,
                    qualification=form.qualification.data,
                    dob=form.dob.data
                )
        # set avatar if provided
        try:
            user.avatar = form.avatar.data
        except Exception:
            pass
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration is successful!', category="success")
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            logging.exception("Failed to create user during registration")
            flash('Registration failed due to server error. Please try again later.', category='danger')
    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.is_admin:
                flash("Admin logged in successfully!", category="success")
                return redirect(url_for("admin.admin_dashboard"))
            else:
                flash('Login successful!', category="success")
                return redirect(url_for('users.dashboard'))
        else:
            flash("Invalid Username or Password!", category="error")
    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout successful!", category="success")
    return redirect(url_for('auth.login'))
