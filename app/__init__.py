#coding:utf-8

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.pagedown import PageDown
from flask.ext.restful import Api
import os
from flask.ext.mail import Mail
from flask.ext.login import LoginManager
from config import basedir
from momentjs import momentjs


app = Flask(__name__, instance_relative_config=True)
api = Api(app)
app.config.from_object('config')
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
lm = LoginManager()
pagedown = PageDown()
pagedown.init_app(app)
lm.init_app(app)
mail = Mail(app)
lm.login_view = 'login'
app.jinja_env.globals['momentjs'] = momentjs

from app import views, models


