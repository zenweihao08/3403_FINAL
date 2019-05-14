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

@app.route("/movies")
def movies():
    movies = Poll.query.all()
    # if(request.accept_mimetypes.accept_html):
    #     return render_template('/movies,',movies=movies)

    date=[{'title':movie.title,'rank':movie.rank} for movie in movies]
    return Response(json.dumps(date), mimetype='application/json')

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


@app.route("/movie/new", methods=['GET', 'POST'])
@login_required
def add_movie():
    form = MoviePollForm()
    if form.validate_on_submit():
        new_movie = MoviePoll(
            movie_title=form.movie_title.data, 
            movie_release_date = form.movie_release_date.data,
            movie_director= form.movie_director.data,
            movie_rank = 0)
        db.session.add(new_movie)
        db.session.commit()
        flash('Your movie is now add to the poll!', 'success')
        return redirect(url_for('movies'))
    return render_template('add_movie.html', title='New Movie',
                           form=form, legend='New Movie')

@app.route("/music/new", methods=['GET', 'POST'])
@login_required
def add_music():
    form = MusicPollForm()
    if form.validate_on_submit():
        new_music = MusicPoll(
            music_title=form.music_title.data,
            music_debut_date = form.music_debut_date.data,
            singer=form.singer.data,
            music_rank=0)
        db.session.add(new_music)
        db.session.commit()
        flash('Your music is now add to the poll!', 'success')
        return redirect(url_for('musics'))
    return render_template('add_music.html', title='New Music',
                           form=form, legend='New Music')

@app.route("/game/new", methods=['GET', 'POST'])
@login_required
def add_game():
    form = GamePollForm()
    if form.validate_on_submit():
        new_game = GamePoll(
            game_title=form.game_title.data,
            game_release_date=form.game_release_date.data, 
            production_company = form.production_company.data)
        db.session.add(new_game)
        db.session.commit()
        flash('Your game is now add to the poll!', 'success')
        return redirect(url_for('games'))
    return render_template('add_game.html', title='New Game',
                           form=form, legend='New Game')

@app.route("/movie/del", methods=['GET','POST'])
@login_required
def del_movie():
    if request.method=='POST':
        movie_id = request.get_json()['id']
        if movie_id:
            del_mov=MoviePoll.query.filter_by(id = movie_id).first()
            db.session.delete(del_mov)
            db.session.commit()
            flash('The movie is now deleted', 'success')
            return redirect(url_for('admin'))
    return render_template('delete_movie.html', title='Delete Movie', legend='Delete Movie')

@app.route("/music/del", methods=['GET', 'POST'])
@login_required
def del_music():
    form = MusicPollForm()
    if form.validate_on_submit():
        del_music = MusicPoll.query.filter_by('music_title=form.music_title.data')
        db.session.delete(del_music)
        db.session.commit()
        flash('The music is now deleted', 'success')
        return redirect(url_for('admin'))
    return render_template('delete_music.html', title='Delete Music',
                           form=form, legend='Delete Music')

@app.route("/game/del", methods=['GET', 'POST'])
@login_required
def del_game():
    form = GamePollForm()
    if form.validate_on_submit():
        del_game = GamePoll.query.filter_by('game_title=form.game_title.data')
        db.session.delete(del_game)
        db.session.commit()
        flash('The game is now deleted', 'success')
        return redirect(url_for('admin'))
    return render_template('delete_game.html', title='Delete Movie',
                           form=form, legend='Delete Movie')

























