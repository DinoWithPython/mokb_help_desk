from flask import (
    render_template, flash, redirect,
    url_for, request, session)
from flask_login import current_user, login_required
from flask_paginate import Pagination, get_page_parameter
import sqlalchemy as sa
from sqlalchemy import func
from app import db
from app.tasks.forms import EditTaskForm, TaskForm, TaskCompleteForm, SearchTask
from app.models import Task
from app.tasks import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = SearchTask()
    # словарь для передачи в шаблон
    content = {}

    # page = request.args.get('page', 1, type=int)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    if form.validate_on_submit():
        if form.submit.data:
            search_string = form.text_search.data
            tasks_bd = Task.query.filter(
                sa.or_(
                    Task.number_task.contains(search_string),
                    Task.theme_task.contains(search_string),
                    Task.tag_task.contains(search_string),
                    Task.person_task.contains(search_string),
                    Task.number_task.contains(search_string.upper()),
                    Task.theme_task.contains(search_string.upper()),
                    Task.tag_task.contains(search_string.upper()),
                    Task.person_task.contains(search_string.upper()),
                    Task.number_task.contains(search_string.capitalize()),
                    Task.theme_task.contains(search_string.capitalize()),
                    Task.tag_task.contains(search_string.capitalize()),
                    Task.person_task.contains(search_string.capitalize()),
                )
            ).order_by(Task.date_create_task.desc())
            count = tasks_bd.count()
            return render_template('index.html', title='Все заявки',
                                   count=count,
                                   form=form,
                                   tasks=tasks_bd,
                                   pagination='')
        if form.cancel.data:
            form = SearchTask('')
            page = 1

    limit = 10
    start = (page-1)*limit
    end = start + limit

    tasks_bd = Task.query.order_by(Task.date_create_task.desc())
    total = tasks_bd.count()
    content['pagination'] = Pagination(page=page, total=total,  
                                       bs_version=4)
    content['tasks'] = tasks_bd.slice(start, end)
    return render_template('index.html', title='Все заявки',
                            form=form, **content)


@bp.route('/active', methods=['GET', 'POST'])
@login_required
def active():
    # словарь для передачи в шаблон
    content = {}
    # page = request.args.get('page', 1, type=int)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # Проверяем есть ли параметр сортировки в запросе
    sort_rule = request.args.get('sort')
    if sort_rule == 'urgency_task':
        tasks_bd = Task.query.filter_by(
            complete=False,
            author_task=current_user
            ).order_by(Task.urgency_task.desc())
    else:
        tasks_bd = Task.query.filter_by(
            complete=False,
            author_task=current_user
            ).order_by(Task.date_create_task.desc())
    total = tasks_bd.count()
    limit = 10
    start = (page-1)*limit
    end = start + limit
    content['pagination'] = Pagination(page=page, total=total,  
                                       bs_version=4)
    content['tasks'] = tasks_bd.slice(start, end)
    return render_template('tasks/tasks_active.html', title='Активные заявки', **content)


@bp.route('/completed', methods=['GET', 'POST'])
@login_required
def completed():
    # словарь для передачи в шаблон
    content = {}
    # page = request.args.get('page', 1, type=int)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    tasks_bd = Task.query.filter_by(
        complete=True,
        author_task=current_user
        ).order_by(Task.date_create_task.desc())

    total = tasks_bd.count()
    limit = 10
    start = (page-1)*limit
    end = start + limit
    content['pagination'] = Pagination(page=page, total=total,  
                                       bs_version=4)
    content['tasks'] = tasks_bd.slice(start, end)
    content['pagination'] = Pagination(page=page, total=total,  
                                       bs_version=4)
    content['tasks'] = tasks_bd.slice(start, end)
    return render_template('tasks/tasks.html', title='Завершенные заявки',
                           **content)


@bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    id_base = db.session.query(func.max(Task.id)).scalar()
    id_base = id_base if id_base else 0
    if form.validate_on_submit():
        task = Task(
            id=id_base+1,
            number_task=form.number_task.data,
            theme_task=form.theme_task.data,
            body_task=form.body_task.data,
            tag_task=form.tag_task.data,
            person_task=form.person_task.data,
            contact_person_task=form.contact_person_task.data,
            author_task=current_user,
            urgency_task=form.urgency_task.data[0]
            )
        db.session.add(task)
        db.session.commit()
        flash('Заявка добавлена')
        return redirect(url_for('tasks.active'))
    return render_template('tasks/create_task.html', title='Создать задачу',
                           form=form)


@bp.route('/task_detail/<task_id>', methods=['GET', 'POST'])
@login_required
def task_detail(task_id):
    task = db.first_or_404(sa.select(Task).where(Task.id == int(task_id)))
    form = TaskCompleteForm()
    if form.validate_on_submit():
        task.complete = True
        task.decision_task = form.decision_task.data
        db.session.commit()
        flash('Изменения успешно сохранены.')
        return render_template(
            'tasks/task_detail.html', task=task,
            title="Подробности заявки")
    elif request.method == 'GET':
        return render_template('tasks/task_detail.html',
                               task=task,
                               title='Выполнить заявку',
                               form=form)


@bp.route('/edit_task/<task_id>/', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = db.first_or_404(sa.select(Task).where(Task.id == int(task_id)))
    if task.author_task != current_user:
        form = TaskCompleteForm()
        flash('Вы не автор заявки. Редактирование запрещено.')
        return render_template('tasks/task_detail.html',
                               task=task,
                               title='Выполнить заявку',
                               form=form)
    if request.method == 'GET':
        form = EditTaskForm()
        form.theme_task.data = task.theme_task
        form.body_task.data = task.body_task
        form.tag_task.data = task.tag_task
        form.person_task.data = task.person_task
        form.contact_person_task.data = task.contact_person_task
        form.urgency_task.data = task.urgency_task
        return render_template('tasks/edit_task.html',
                                task=task,
                                title='Изменить заявку',
                                form=form)
    if request.method == 'POST':
        form = TaskCompleteForm()
        task.theme_task = request.form.get('theme_task')
        task.body_task = request.form.get('body_task')
        task.tag_task = request.form.get('tag_task')
        task.person_task = request.form.get('person_task')
        task.contact_person_task = request.form.get('contact_person_task')
        task.urgency_task = request.form.get('urgency_task')
        db.session.commit()
        flash('Изменения успешно сохранены.')
        return redirect(url_for('tasks.task_detail', task_id=task.id))

