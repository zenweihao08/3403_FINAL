import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, json, Response
from flaskpoll import app, db, bcrypt
from flaskpoll.forms import RegistrationForm, LoginForm, UpdateAccountForm, MoviePollForm, MusicPollForm, GamePollForm
from flaskpoll.models import User, Poll
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

@app.route("/")
@app.route("/home")
def home():
    movies = Poll.query.all()
    [i.calculation_url_and_other() for i in movies]

    movies.sort(key=lambda movie: movie.rank,reverse=True);
    return render_template('home.html', movies=movies, title='Home',)

@app.route('/movies')
def movies():
    movies = Poll.query.all()
    # if(request.accept_mimetypes.accept_html):
    #     return render_template('/movies,',movies=movies)

    date=[{'title':movie.title,'rank':movie.rank,'image_url':movie.image_url} for movie in movies]
    return Response(json.dumps(date), mimetype='application/json')

@app.route('/chart')
def chart():
    return render_template('chart.html',title='Chart')


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/admin")
@login_required
def admin():
    if(not User.is_admin()):
        return redirect('home')

    movies = Poll.query.all()
    users = User.query.all()

    return render_template('admin.html', movies=movies, users = users,title='Admin')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/add_poll", methods=['GET', 'POST'])
@login_required
def add_poll():
    if request.method=="POST":
        form =request.form
        new_movie = Poll(
            title=form['title'] ,
            release_date = datetime.strptime(form['date'] ,'%Y-%m-%d').date(),
            introduction= form['introduction'],
            rank = 0,
            image_url=form['image_url'],
            initiator=current_user.id)

        db.session.add(new_movie)
        db.session.commit()
        flash('Your movie is now add to the poll!', 'success')
        return redirect(url_for('admin'))
    return render_template('add_poll.html',title='Add Poll')

@app.route("/poll", methods=['GET', 'POST'])
@login_required
def poll():

    user=User.query.filter_by(id=current_user.id).first()

    if user.voted:
        return redirect('/home')

    movie_id = request.args['movie_id']
    user.cast_to=movie_id
    user.voted=True
    movie=Poll.query.filter_by(id = movie_id).first()
    movie.rank+=1


    db.session.commit()

    return redirect(url_for('home'))

@app.route("/unpoll", methods=['GET', 'POST'])
@login_required
def unpoll():

    movie_id = request.args['movie_id']

    movie=Poll.query.filter_by(id = movie_id).first()
    movie.rank-=1

    user=User.query.filter_by(id=current_user.id).first()
    user.cast_to=None
    user.voted=False
    db.session.commit()

    return redirect(url_for('home'))

@app.route("/reset_vote", methods=['GET', 'POST'])
@login_required
def reset_vote():

    user=User.query.filter_by(id=request.args['id']).first()
    movie=Poll.query.filter_by(id = user.cast_to).first()
    if movie:

        movie.rank-=1
        user.cast_to=None
        user.voted=False

        db.session.commit()

        flash('reset success')

    return redirect(url_for('admin'))

@app.route("/del/movie", methods=['GET','POST'])
@login_required
def del_movie():

    movie_id = request.args['id']
    if movie_id and User.is_admin():
        for user in User.query.filter_by(cast_to=movie_id).all():
            user.voted=False
            user.cast_to=None

        del_mov=Poll.query.filter_by(id = movie_id).first()
        db.session.delete(del_mov)
        db.session.commit()
        flash('The movie is now deleted', 'success')
        return redirect(url_for('admin'))

    return redirect('/home')


@app.route("/del/user")
@login_required
def del_user():
    id=request.args['id']
    if(id and User.is_admin()):

        user = User.query.filter_by(id=id).first()
        if user.voted:
            movie=Poll.query.filter_by(id = user.cast_to).first()
            movie.movie_rank-=1;

        db.session.delete(user)
        db.session.commit()
        flash('The user is now deleted', 'success')

        return redirect('/admin')

    return Response(json.dumps(False),mimetype='application/json')


























