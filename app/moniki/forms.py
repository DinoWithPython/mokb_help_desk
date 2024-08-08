from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Length
import sqlalchemy as sa
from app import db


class MonikiForm(FlaskForm):
    number_research = IntegerField(
        'Номер направления',
        validators=[DataRequired('Укажите номер направления и убедитесь, что в нём цифры!')])
    specialty = StringField(
        'Специальность')
    specific = StringField(
        'Специфика(для ввода фио врача укажите "ФИО: ", если фио несколько, то через пробел с запятой "авп, Павлов, Сид")')
    comment = StringField(
        'Имя, кто обратился')
    submit = SubmitField('Сохранить')

    def validate_specialty(self, specialty):
        specialty_d = {
            "Акушерство и гинекология": 0,
            "Аллергология и иммунология": 0,
            "Гастроэнтерология": 0,
            "Гематология": 0,
            "Инфекционные болезни": 0,
            "Кардиология": 0,
            "Колопроктология": 0,
            "Лабораторная диагностика": 0,
            "Неврология": 0,
            "Нейрохирургия": 0,
            "Нефрология": 0,
            "Онкология": 0,
            "Оториноларингология": 0,
            "Офтальмология": 0,
            "Психотерапия": 0,
            "Пульмонология": 0,
            "Ревматология": 0,
            "Сердечно-сосудистая хирургия": 0,
            "Стоматология общей практики": 0,
            "Стоматология терапевтическая": 0,
            "Стоматология хирургическая": 0,
            "Сурдология-оториноларингология": 0,
            "Терапия": 0,
            "Торакальная хирургия": 0,
            "Травматология и ортопедия": 0,
            "Ультразвуковая диагностика": 0,
            "Урология": 0,
            "Функциональная диагностика": 0,
            "Хирургия": 0,
            "Челюстно-лицевая хирургия": 0,
            "Эндокринология": 0,
        }
        if self.specialty.data not in specialty_d:
            raise ValidationError("Нет такой специальности в МОНИКИ. Проверьте данные.")

