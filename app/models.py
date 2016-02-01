#coding:utf-8
from app import app, db
from markdown import markdown
import bleach
from werkzeug.security import generate_password_hash, check_password_hash

import sys
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask.ext.whooshalchemy as whooshalchemy

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    hash_psw = db.Column(db.String(128))
    email = db.Column(db.String(128))
    email_confirm = db.Column(db.Boolean)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    essays = db.relationship('Essay', backref='author', lazy='dynamic')
    followed = db.relationship('User',
        secondary = followers,
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers', lazy = 'dynamic'),
        lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_annoyous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def generate_psw(self, password):
        self.hash_psw = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.hash_psw, password)


    def avatar(self, size):
        return 'http://7xpqi6.com1.z0.glb.clouddn.com/avatar' + str(int(self.id)%23 + 6) + '.png-size' + str(size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def user_to_json(self):
        json_user = {
            "user_id": self.id,
            "nickname": self.nickname,
            "about_me": self.about_me,
            "last_seen": self.last_seen
        }
        return json_user


    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Post(db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def post_to_json(self):
        json_post = {
            "post_id": self.id,
            "body": self.body,
            "timestamp": self.timestamp,
            "author": self.author.nickname
        }
        return json_post

    def __repr__(self):
        return '<Post %r>' % (self.body)

class Essay(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags=['a','abbr','acronym','b','blockqoute','code','em','i','li','ol','pre','strong','ul','h1','h2','h3','p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


    def __repr__(self):
        return '<Essay No.%d>' % (self.id)

if enable_search:
    whooshalchemy.whoosh_index(app, Post)

db.event.listen(Essay.body, 'set', Essay.on_changed_body)
