from datetime import datetime, timezone
from flask import (
    render_template, flash, redirect, url_for,
    request, current_app)
from flask_login import current_user, login_required
import sqlalchemy as sa
from app import db
from app.main.forms import (
    EditProfileForm,
    EmptyForm, PostForm)
from app.models import User, Post, Task
from app.main import bp
from app.tools import paginate_tool


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/my_notes', methods=['GET', 'POST'])
@login_required
def my_notes():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Ваш пост на информационном пространстве :)')
        return redirect(url_for('main.my_notes'))
    page = request.args.get('page', 1, type=int)

    data = paginate_tool(
        data=current_user.following_posts(),
        page=page,
        url='main.my_notes',
        name='posts'
    )
    return render_template('posts.html', title='Главнющая', form=form,
                           **data)


@bp.route('/notes')
@login_required
def notes():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    data = paginate_tool(
        data=query,
        page=page,
        url='main.notes',
        name='posts')
    return render_template('posts.html', title='Все заметки',
                           **data)


@bp.route('/delete_post/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    author = db.first_or_404(Post.query.filter_by(id=int(id))).author
    post = db.first_or_404(sa.select(Post).where(Post.id == int(id)))
    if current_user == author:
        db.session.delete(post)
        db.session.commit()
        flash('Заметка удалена')
        return redirect(url_for('main.notes'))
    else:
        flash('Удаление чужих записей запрещено!')
        return redirect(url_for('main.notes'))


@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    tasks_complete = Task.query.filter_by(
        complete=True,
        author_task=user
        ).count()
    tasks_not_complete = Task.query.filter_by(
        complete=False,
        author_task=user
        ).count()
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for(
        'main.user', username=user.username, page=posts.next_num
        ) if posts.has_next else None
    prev_url = url_for(
        'main.user', username=user.username, page=posts.prev_num
        ) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form,
                           tasks_complete=tasks_complete,
                           tasks_not_complete=tasks_not_complete)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Изменения успешно сохранены.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Редактировать профиль',
                           form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'Пользователь {username} не сущестует.')
            return redirect(url_for('tasks.index'))
        if user == current_user:
            flash('Вы не можете подписаться на себя.')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'Вы подписаны на {username}!')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('tasks.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'Пользователь {username} не сущестует.')
            return redirect(url_for('tasks.index'))
        if user == current_user:
            flash('Вы не можете подписаться на себя.')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'Вы отписались от {username}.')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('tasks.index'))
