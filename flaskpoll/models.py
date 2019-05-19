import json
import string
from datetime import datetime
from flaskpoll import db, login_manager
from flask_login import UserMixin
from flask_login import  current_user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    voted=db.Column(db.Boolean, nullable=False,default=False)
    cast_to=db.Column(db.Integer,default=None)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    @staticmethod
    def is_admin():
        with open('admin.json', 'r') as f:
            admin_id_list = json.load(f)
            return current_user.id in admin_id_list;
        return False;


class Poll(db.Model):
    url=None;
    icon='';
    btn_text=None

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    introduction = db.Column(db.String(1000), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rank = db.Column(db.Integer)
    initiator=db.Column(db.Integer,nullable=False)

    def calculation_url_and_other(self):

        if current_user.is_authenticated:
            if current_user.voted:
                self.url ,self.btn_text,self.icon =('/unpoll' ,'Withdraw Your Vote',"") if current_user.cast_to==self.id else ('/about','Vote For It',"disabled")
            else:
                self.url,self.btn_text=('/poll','Vote For It')

            self.url+='?movie_id='+str(self.id)
        else:
            self.url='/register'
            self.icon=''
            self.btn_text='Vote For It'

db.create_all()

