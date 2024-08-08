from flask import Blueprint

bp = Blueprint('moniki', __name__)

from app.moniki import routes