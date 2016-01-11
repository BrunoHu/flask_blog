#!/flask/bin/python
#coding:utf-8

from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm, RegisterForm, EditForm, PostForm, SearchForm
from .models import User, Post
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, MAX_INT
import random
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    user = g.user
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    posts = user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template("index.html", title='Home', form=form, user=user, posts=posts)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        remember_me = False
        session['remember_me'] = form.remember_me.data
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        login_user(user, remember = remember_me)
        return redirect('/index')
    return render_template('login.html',
        title = 'Sign In',
        form = form)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
        flash(u'成功注册')
        login_user(user)
        return redirect('index')
    return render_template('register.html',title='Sign Up', form=form)

@app.before_request
def before_request():
    g.user = current_user

    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()

@app.route('/logout')
def logout():
    session.pop('_flashes', None)
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash(u'哎呀，找不到这个家伙')
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash(u'修改成功')
        return redirect(url_for('edit'))
    else:
        form.about_me.data = g.user.about_me
    return render_template('edit.html', user=g.user, form=form)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('用户 %s 不存在.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('你不能关注自己')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('无法关注'+nickname)
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('成功关注' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('用户 %s 不存在.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('你不能取消关注自己')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('无法取消关注'+nickname)
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('您已取消关注' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))

@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query = g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
        query = query,
        results = results)

@app.route('/random_find')
@login_required
def random_find():
    users = User.query.all()
    random_seed = random.randint(1,MAX_INT) % len(users)
    user = users[random_seed]
    return redirect(url_for('user', nickname=user.nickname))

@app.route('/log')
def log():
    return render_template('log.html')


