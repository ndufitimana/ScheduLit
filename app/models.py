from datetime import datetime, timedelta
from email.mime import base
from email.policy import default
from encodings import utf_8
from hmac import digest
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from app import db, login
from flask import current_app
from flask import url_for
import os, base64



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
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

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

    def to_dict(self, include_email = False):
        """
        this function returns a user representation in a dictionary format.
        This user representation is used by our api
        """
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat()+ 'Z', #turns it in utc
            'about_me': self.about_me,
            'follower_count': self.followers.count(),
            '_links': {
                'self': url_for('api.get_user', id = self.id),
                'followers':url_for('api.get_followers', id= self.id),
                'avatar': self.avatar(128)


            }

        }
        if include_email:
            data['email'] = self.email
        return data
    def from_dict(self, data, new_user=False):
        """This function gets data from the request and makes changes to db
        as requested"""
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    """ This next module allows support for tokens in our api """
    def get_token(self, expires_in=3600):
        now= datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now+timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    def revoke_token(self):
        self.token_expiration=datetime.utcnow() - timedelta(seconds=1)
    @staticmethod
    def check_token(token):
        user= User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
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


    

