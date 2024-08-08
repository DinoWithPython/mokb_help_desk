from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import (
    LoginForm, RegistrationForm,
    ResetPasswordRequestForm, ResetPasswordForm)
from app.models import User
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Некорректное имя или пароль.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('tasks.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Войти', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('tasks.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, теперь вы в ИТ банде!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Регистрация',
                           form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Поверьте вашу почту и следуйте указаниям из инструкции.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Сбросить пароль', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('tasks.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('tasks.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Ваш пароль был сброшен!')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
