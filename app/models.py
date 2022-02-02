from datetime import datetime
from email.policy import default
from hmac import digest
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from app import db, login
from flask import current_app





followers = db.Table('followers', 
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')) 
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(64), index = True)
    last_name = db.Column(db.String(100), index = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    courses = db.relationship('Course', backref ='author', lazy = 'dynamic')
    about_me = db.Column(db.String(150))
    last_seen = db.Column(db.DateTime, default= datetime.utcnow)
    #the following part defined the followers-followed relationship
    followed = db.relationship('User', secondary = followers,
        primaryjoin =(followers.c.follower_id == id), 
        secondaryjoin=(followers.c.followed_id == id), 
        backref = db.backref('followers', lazy= 'dynamic'), lazy = 'dynamic' )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    def getCourses(self):
        my_courses = Course.query.filter_by(user_id = self.id)
        return my_courses
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count()>0
    def followed_courses(self):
        followed = Course.query.join(
            followers, (followers.c.followed_id == Course.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Course.query.filter_by(user_id= self.id)
        return followed.union(own).order_by(Course.timestamp.desc())


    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)
class Course(db.Model):
    #this class will represent the courses added by the user
    id = db.Column(db.Integer, primary_key = True)
    course = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, index = True, default= datetime.utcnow)
    building = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    
    def __repr__(self):
        return '<Course {}>'.format(self.course)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


    

