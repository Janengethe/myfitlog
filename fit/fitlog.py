from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from fit.auth import login_required
from fit.db import get_db

bp = Blueprint('fitlog', __name__)


@bp.route('/')
def index():
    return render_template('fitlog/index.html')


@bp.route('/all')
@login_required
def all():
    db = get_db()
    workouts = db.execute(
        'SELECT w.id, exercise, notes, created, user_id, username'
        ' FROM workout w JOIN user u ON w.user_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('fitlog/all.html', workouts=workouts)




# @bp.route('/<int:id>/added', methods=('GET', 'POST'))
# @login_required
# def added():
#     one = get_db().execute(
#         'SELECT w.id, exercise, notes, created, user_id, username'
#         ' FROM workout w JOIN user u ON w.user_id = u.id'
#         ' ORDER BY created DESC'
#     ).fetchone()

#     return render_template('fitlog/added.html', one=one)




@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        exercise = request.form['exercise']
        notes = request.form['notes']
        error = None

        if not exercise:
            error = 'This field is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO workout (exercise, notes, user_id)'
                ' VALUES (?, ?, ?)',
                (exercise, notes, g.user['id'])
            )
            db.commit()
            return redirect(url_for('fitlog.all'))

    return render_template('fitlog/create.html')


def get_one(id, check_user=True):
    workout = get_db().execute(
        'SELECT w.id, exercise, notes, created, user_id, username'
        ' FROM workout w JOIN user u ON w.user_id = u.id'
        ' WHERE w.id = ?',
        (id,)
    ).fetchone()

    if workout is None:
        abort(404, f"Workout id {id} doesn't exist.")

    if check_user and workout['user_id'] != g.user['id']:
        abort(403)

    return workout




@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    workout = get_one(id)

    if request.method == 'POST':
        exercise = request.form['exercise']
        notes = request.form['notes']
        error = None

        if not exercise:
            error = 'Workout is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE workout SET exercise = ?, notes = ?'
                ' WHERE id = ?',
                (exercise, notes, id)
            )
            db.commit()
            return redirect(url_for('fitlog.all'))

    return render_template('fitlog/update.html', workout=workout)




@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_one(id)
    db = get_db()
    db.execute('DELETE FROM workout WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('fitlog.all'))