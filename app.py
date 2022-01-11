from flask import Flask, request, render_template, flash, redirect, render_template, jsonify, session
import psycopg2
from flask_debugtoolbar import DebugToolbarExtension 
from models import connect_db, db, User, Feedback
from flask_bcrypt import Bcrypt
from forms import RegisterForm, LoginForm, AddFeedback, UpdateFeedback

bcrypt = Bcrypt()


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "topsecret1"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


connect_db(app)


@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/users/<username>')
def show_secrets(username):
    if "user_id" not in session:
        return redirect('/')
    user = User.query.get(username)
    return render_template('secrets.html', user)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        # db.session.add(new_user)
        # db.session.commit()
        session['user_id'] = new_user.username
    
        return redirect('/users/<username>')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user.username

            return redirect(f'/users/{user.username}')
        else:
            form.username.errors=["Invalid username or password. Please try again."]
    
    return render_template('login.html')

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if "user_id" not in session:
        return redirect('/')
    form = AddFeedback()
    user = User.query.get(username)
    if form.validate_on_submit():
        feedback = Feedback(
            title=form.title.data,
            content=form.content.data,
            username=username
        )
        db.session.add(feedback)
        db.session.commit()
        return redirect(f'/users/{username}')
        
    
   
    return render_template('add_feedback.html', user=user, form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    if "user_id" not in session:
        return redirect('/')
    form = UpdateFeedback()
    feedback = Feedback.query.get(feedback_id)
    if form.validate_on_submit():
        feedback.content= form.content.data
        feedback.title= form.title.data
        db.session.commit()
        return redirect(f'/users/{feedback.username}')


    return render_template('update_feedback.html', feedback=feedback, form=form)


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    if "user_id" not in session:
        return redirect('/')
    feedback = Feedback.query.get(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{feedback.username}')


    
    
    
    