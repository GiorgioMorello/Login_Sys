from flask import render_template, url_for, redirect, session, request, flash
from login_system import app, bcrypt, db
import uuid
from login_system.forms import Profile
import os
from functools import wraps
import secrets
from PIL import Image


# If the user isn't logged in, he will be redirected to the log in page or the creation page
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)

        else:
            flash('Create an account or Log in', 'alert-info')
            return redirect(url_for('login'))
    return wrap


def save_image(image):
    # So that the names aren't the same, add a code inside the filename
    cod = secrets.token_hex(8)
    name, extension = os.path.splitext(image.filename)
    file_name = name + cod + extension
    full_path = os.path.join(app.root_path, 'static/profile_pic', file_name) # The path will be where the file will be inserted

    # this is where the image will be processed
    size = (200, 200)
    reduced_image = Image.open(image)
    reduced_image.thumbnail(size)
    reduced_image.save(full_path)
    return file_name


@app.route('/', methods=['POST', 'GET'])
@login_required
def home():
    profile_pic = ''
    form_p = Profile()
    if 'logged_in' in session:
        session_user = session['_id']
        user = db.User.find_one({'_id': session_user})

# If the user clicks the submit button and the file field is filled in
# the profile pic will be processed and stored in the DB
        if form_p.validate_on_submit() and form_p.profile_pic.data:
            profile_pic = save_image(form_p.profile_pic.data)
            db.User.update_one(user, {'$set': {'pic': profile_pic}})

    profile_pic = url_for('static', filename=f'profile_pic/{user["pic"]}')

    return render_template('home.html', user=user, form_p=form_p, profile_pic=profile_pic)



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.User.find_one({'email': email})
        try:
            if user['email'] == email and bcrypt.check_password_hash(user['password'], password):
                session['logged_in'] = True
                session['_id'] = user['_id']
                flash('Welcome', 'alert-success')
                return redirect(url_for('home'))
            else: # If the user doesn't exist, an error message will appear
                flash("Invalid credentials", 'alert-danger')
        except: # If another type of error occurs, an error message will appear
            flash("Invalid credentials", 'alert-danger')

    return render_template('login.html')



@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        _id = uuid.uuid4().hex
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_c = request.form.get('password_c')
        profile_pic = 'default.jpg'
        existing_user = db.User.find_one({'email': email})
        if len(username) < 2:
            flash("Name must be at least 2 characters", 'alert-danger')
        elif not ".com" in email or len(email) < 5:
            flash("Incorret Email", 'alert-danger')
        elif len(password) < 6:
            flash("Password must be at least 6 characters", 'alert-danger')
        elif password_c != password:
            flash("Passwords Don't match", 'alert-danger')
        else:
            if existing_user == None:
                encrypt_password = bcrypt.generate_password_hash(password)
                user = db.User.insert_one({'_id': _id, 'username': username, 'email': email, 'password': encrypt_password, 'pic': profile_pic})
                session['logged_in'] = True
                session['_id'] = _id
                flash('User created', 'alert-success')
                return redirect(url_for('home'))
            else:
                flash('This email is already in use', 'alert-danger')

    return render_template('create.html')


@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/delete/<id>')
def delete(id):
    user_id = id
    session.clear()
    db.User.delete_one({'_id': user_id})
    flash('Your account has been removed', 'alert-info')
    return redirect(url_for('login'))