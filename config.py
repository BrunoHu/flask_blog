#coding:utf-8

import os

CSRF_ENABLED = True

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

POSTS_PER_PAGE = 5

WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50
MAX_INT = 1000000

MAIL_DEFAULT_SENDER = (u'Bavel管理员','bavel_arnold@sina.com')
FLASKY_MAIL_SUBJECT_PREFIX = '[Bavel]'
