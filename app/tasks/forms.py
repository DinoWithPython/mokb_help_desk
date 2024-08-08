from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
import sqlalchemy as sa
from app import db
from app.models import Task


class TaskForm(FlaskForm):
    number_task = StringField(
        'Номер заявки',
        validators=[DataRequired('Укажите номер заявки!')])
    theme_task = StringField(
        'Тема заявки',
        validators=[DataRequired('Не указана тема заявки.')])
    body_task = TextAreaField(
        'Копия текста заявки',
        validators=[DataRequired('Заполните тело заявки.')])
    tag_task = StringField(
        'Введите основные тэги',
        validators=[DataRequired('Теги нужны для поиска.')])
    person_task = StringField(
        'Имя заявителя',
        validators=[DataRequired('Для кого заявка')])
    contact_person_task = StringField(
        'Контакты персоны',
        validators=[DataRequired('А кому потом сообщать будем?')])
    urgency_task = SelectMultipleField(
        'Срочность',
        choices=[('1', 'Низкая'), ('2', 'Средняя'), ('3', 'Высокая')],
        validators=[DataRequired('Укажите срочность заявки.')]
    )
    submit = SubmitField('Сохранить')

    def validate_number_task(self, number_task):
        task = db.session.scalar(sa.select(Task).where(
            Task.number_task == self.number_task.data))
        if task is not None:
            raise ValidationError('Такой номер заявки уже существует.')

class EditTaskForm(FlaskForm):
    theme_task = StringField(
        'Тема заявки',
        validators=[DataRequired('Не указана тема заявки.')])
    body_task = TextAreaField(
        'Копия текста заявки',
        validators=[DataRequired('Заполните тело заявки.')])
    tag_task = StringField(
        'Введите основные тэги',
        validators=[DataRequired('Теги нужны для поиска.')])
    person_task = StringField(
        'Имя заявителя',
        validators=[DataRequired('Для кого заявка')])
    contact_person_task = StringField(
        'Контакты персоны',
        validators=[DataRequired('А кому потом сообщать будем?')])
    urgency_task = SelectMultipleField(
        'Срочность',
        choices=[('1', 'Низкая'), ('2', 'Средняя'), ('3', 'Высокая')],
        validators=[DataRequired('Укажите срочность заявки.')]
    )
    submit = SubmitField('Сохранить')


class TaskCompleteForm(FlaskForm):
    decision_task = TextAreaField(
        'Введите исход заявки:',
        validators=[Length(min=0, max=1400)]
        )
    submit = SubmitField('Завершить')


class SearchTask(FlaskForm):
    text_search = StringField(
        'Что ищем? (номер, тему,тэг или для кого)',
        validators=[DataRequired('Поле не может быть пустым.')])
    submit = SubmitField('Найти')
    cancel = SubmitField('Очистить')
