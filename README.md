# МОКБ простенький проект на фласке для учета своих заявок
Изучаю фласк по книге: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world


Для работы требуется БД по скрипту из МОНИКИ

* Необходимо наличие файла `config.py`
```
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['ваша почта']
    POSTS_PER_PAGE = 10
    PER_PAGE = 10
```

* В файле `.env`:
```
MAIL_SERVER=smtp.rambler.ru
MAIL_PORT=465
MAIL_USE_TLS=yes
MAIL_USERNAME=
MAIL_PASSWORD=
DIR_MONIKI_BASE =
DIR_MONIKI_BASE_ANL =
```

Поскольку база была SQLite, то нужна её копия для вывода текущих не записанных пациентов. Если перевести это на другую БД, то код можно упростить.

* Затем инициализируем/обновляем БД фласка
`flask db upgrade`

* Запускаем приложение
`flask run`

* Для отображения даты на русском, нужно немного поправить исходники в модулях, типа flask_moment.
В функции flask_moment_js() заменить возврат из функции "en" на "ru". Потому что в этом случае не удасться никак переопределить язык, ведь он всегда возвращается инглишом.

* Схемы баз данных:

![Схема бд фласка](https://github.com/DinoWithPython/mokb_help_desk/blob/main/schemes_jpg/flask_bd.png)
![Схема бд МОНИКИ](https://github.com/DinoWithPython/mokb_help_desk/blob/main/schemes_jpg/Схема%20БД%20МОНИКИ.png)