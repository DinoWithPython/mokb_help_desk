from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
import sqlalchemy as sa
from app import db
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(
        'Имя пользователя',
        validators=[DataRequired('Не может быть пустым!')])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Сохранить')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == self.username.data))
            if user is not None:
                raise ValidationError('Пожалуйста, введите другое имя.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Отправить')


class PostForm(FlaskForm):
    post = TextAreaField(
        'Напиште что-то',
        validators=[DataRequired('Ну хоть что-то!')])
    submit = SubmitField('Отправить')
