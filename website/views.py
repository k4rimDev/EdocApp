from cmath import exp
from fileinput import filename
from flask import Flask, Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from . import db
from .models import Note


from website import create_app

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        if Note.query.filter(Note.data.contains(request.form['q'])):
            document = Note.query.filter(Note.data.contains(request.form['q'])).first()            
            return render_template('index.html', download_name = document.data, download_document = document.data_path, user=current_user)
        else:
            return render_template('index.html', download_name = 'Not found!', user=current_user)

    return render_template('index.html', user=current_user)




# Upload file to document folder
class UploadFileForm(FlaskForm):
    file = FileField('File', validators=[InputRequired()])
    submit = SubmitField('Upload File')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'kerim123'
app.config['UPLOAD_FOLDER'] = 'static/documents'

@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():

    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], str(secure_filename(file.filename)).lower()))
        if request.method == 'POST':
            data_name = str(secure_filename(file.filename))[:len(str(secure_filename(file.filename))) - 4].lower()
            data_path = 'static/documents/' + str(secure_filename(file.filename)).lower()

            new_data = Note(data = data_name, data_path = data_path)
            db.session.add(new_data)
            db.session.commit()

            return redirect(url_for('views.home'))

        return 'File has been uploaded'

    if request.method == 'POST':
        if Note.query.filter(Note.data.contains(request.form['q'])):
            document = Note.query.filter(Note.data.contains(request.form['q'])).first()            
            return render_template('home.html', download_name = document.data, download_document = document.data_path, user=current_user, form=form)
        else:
            return render_template('home.html', download_name = 'Not found!', user=current_user, form=form)

    return render_template('home.html',
                            user = current_user,
                            form=form)

