from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(
        'Имя пользователя',
        validators=[DataRequired('Поле не может быть пустым!')])
    password = PasswordField(
        'Пароль',
        validators=[DataRequired('Поле не может быть пустым!')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField(
        'Имя пользователя',
        validators=[DataRequired('Поле не может быть пустым!')])
    email = StringField(
        'Электронная почта',
        validators=[DataRequired('Поле не может быть пустым!'), Email()])
    password = PasswordField(
        'Пароль',
        validators=[DataRequired('Поле не может быть пустым!')])
    password2 = PasswordField(
        'Повторите пароль',
        validators=[DataRequired('Поле не может быть пустым!'),
                    EqualTo('password')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Пожалуйста, введите другое имя.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Пожалуйста, введите другую почту.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        'Электронная почта',
        validators=[DataRequired('Поле не может быть пустым!'), Email()])
    submit = SubmitField('Сбросить пароль')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'Пароль',
        validators=[DataRequired('Поле не может быть пустым!')])
    password2 = PasswordField(
        'Повторите пароль',
        validators=[DataRequired('Поле не может быть пустым!'),
                    EqualTo('password')])
    submit = SubmitField('Сбросить пароль')
