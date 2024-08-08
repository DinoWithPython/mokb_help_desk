from datetime import datetime as d
import os.path
import os
import shutil
import sqlite3

import pandas as pd
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.moniki.forms import MonikiForm
from app.moniki import bp

def put_record(
        cur,
        number_direct: str,
        specialty: str,
        is_recorded: int,
        date_direct: str = None,
        time_direct: str = None,
        date_changes: str = None,
        specific: str = None,
        comment: str = None,
        notified: bool = False
        ):
    """Добавляет в таблицу moniki_records новое направление для отслеживания."""
    record = (
        d.now(), number_direct, specialty, is_recorded, date_direct,
        time_direct, date_changes, specific, comment, notified)
    cur.execute("""
        INSERT INTO moniki_records VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", record)

def get_numbers_direct(cur):
    """Возвращает список всех направлений."""
    try:
        cur.execute("""SELECT number_direct FROM moniki_records""")
        data = cur.fetchall()
        data = [x[0] for x in data]
    finally:
        return data


@bp.route('/add_moniki', methods=['GET', 'POST'])
@login_required
def add_moniki():
    DIR_MONIKI_BASE = os.environ.get('DIR_MONIKI_BASE')
    form = MonikiForm()
    if form.validate_on_submit():
        number_research=form.number_research.data,
        specialty=form.specialty.data,
        specific=form.specific.data,
        comment=form.comment.data
        with sqlite3.connect(DIR_MONIKI_BASE) as conn:
            cur = conn.cursor()
            if str(number_research[0]) in get_numbers_direct(cur):
                flash('Направление с таким номером уже существует!')
            if specific == '':
                put_record(cur, number_research[0], specialty[0].strip(), 0, comment=comment.strip())
            else:
                put_record(
                    cur, number_research[0], specialty[0].strip(), 0,
                    specific=specific[0].strip(), comment=comment.strip())
            conn.commit()
        flash('Заявка добавлена')
        return redirect(url_for('moniki.add_moniki'))
    return render_template('moniki/add_moniki.html', title='Добавить направление',
                           form=form)


@bp.route('/not_notified', methods=['GET', 'POST'])
@login_required
def not_notified():
    DIR_MONIKI_BASE = os.environ.get('DIR_MONIKI_BASE')
    DIR_MONIKI_BASE_ANL = os.environ.get('DIR_MONIKI_BASE_ANL')
    shutil.copyfile(DIR_MONIKI_BASE, DIR_MONIKI_BASE_ANL)
    conn = sqlite3.connect(DIR_MONIKI_BASE_ANL)
    need_record = pd.read_sql_query(
        'SELECT * FROM moniki_records',
        conn
    )
    need_record['date_adding'] = pd.to_datetime(need_record['date_adding'], format='mixed')
    not_notified = need_record[need_record['notified'] == 0]
    return render_template(
        'moniki/not_notified.html',
        title='Направления без оповещения',
        row_data=list(not_notified.values.tolist()),
        )


@bp.route('/notify/<int:number>', methods=['GET', 'POST'])
@login_required
def notify(number):
    DIR_MONIKI_BASE = os.environ.get('DIR_MONIKI_BASE')
    with sqlite3.connect(DIR_MONIKI_BASE) as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE moniki_records SET notified = (?) WHERE number_direct = (?)""",
            (1, number)
        )
        conn.commit()
    flash('Отметка об оповещении проставлена')
    return redirect(url_for('moniki.not_notified'))


@bp.route('/chg_status/<int:number>', methods=['GET', 'POST'])
@login_required
def chg_status(number):
    DIR_MONIKI_BASE = os.environ.get('DIR_MONIKI_BASE')
    with sqlite3.connect(DIR_MONIKI_BASE) as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT is_recorded FROM moniki_records WHERE number_direct = (?)""",
            (number,)
        )
        now_status = cur.fetchone()[0]
        if now_status:
            cur.execute(
                """UPDATE moniki_records SET is_recorded = (?) WHERE number_direct = (?)""",
                (0, number)
            )
        else:
            cur.execute(
                """UPDATE moniki_records SET is_recorded = (?) WHERE number_direct = (?)""",
                (1, number)
            )
        conn.commit()
    flash('Статус изменен!')
    return redirect(url_for('moniki.not_notified'))
