
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, User, History
from . import db
from datetime import datetime

views = Blueprint('views', __name__)

    
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id) 
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
            
            history = History(user_id=current_user.id, note_id=new_note.id, operation_type='create')
            db.session.add(history)
            db.session.commit()

    return render_template("home.html", user=current_user)

@views.route('/edit_note/<note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    note = Note.query.get(note_id)
    if request.method == 'POST':
        note.data = request.form['data']
        user_id = current_user.id
        history = History(user_id=user_id, note_id=note_id, operation_type='edit')
        db.session.add(history)
        db.session.commit()
        return redirect(url_for('views.show_notes'))
    return render_template('edit_note.html', note=note, user=current_user)

@views.route('/show_notes', methods=['GET'])
@login_required
def show_notes():
    users = User.query.all()
    return render_template("show_notes.html", users=users, user=current_user)

@views.route('/note_history/<note_id>', methods=['GET'])
@login_required
def note_history(note_id):
    note = Note.query.get(note_id)
    history = History.query.filter_by(note_id=note_id).order_by(History.timestamp.desc()).all()
    return render_template('note_history.html', note=note, history=history, user=current_user)

@views.route('/delete_note/<int:note_id>/', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    if note.user_id != current_user.id:
        flash("You don't have permission to delete this note.", category='error')
    else:
        user_id = current_user.id
        history = History(user_id=user_id, note_id=note_id, operation_type='delete')
        db.session.add(history)
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully.', category='success')
    
    return redirect(url_for('views.show_notes'))