#!/flask/bin/python
#coding:utf-8

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm, RegisterForm, EditForm, PostForm, SearchForm, EssayForm
from .models import User, Post, Essay
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, MAX_INT
import random
import jieba



@app.route('/test')
def test():
    return render_template('test.html')



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
        user = User(nickname=form.nickname.data)
        user.generate_psw(form.password.data)
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

    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    essays = user.essays.order_by(Essay.timestamp.desc())
    return render_template('user.html', user=user, posts=posts, essays=essays)

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
        flash(u'用户 %s 不存在.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash(u'你不能关注自己')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash(u'无法关注'+nickname)
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(u'成功关注' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(u'用户 %s 不存在.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash(u'你不能取消关注自己')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash(u'无法取消关注'+nickname)
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(u'您已取消关注' + nickname + '.')
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

@app.route('/documents/log')
def log():
    return render_template('log.html')

@app.route('/api/user/<nickname>/posts/')
def get_posts(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    posts = user.posts
    return jsonify({'posts': [post.post_to_json() for post in posts]})

@app.route('/api/user/<nickname>/followed_posts/')
def all_followed_posts(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    posts = user.followed_posts()
    return jsonify({'followed posts': [post.post_to_json() for post in posts]})

@app.route('/api/posts/')
def all_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return jsonify({'all posts': [post.post_to_json() for post in posts]})

@app.route('/documents/api_v1.0')
def api_v1():
    return render_template('api_v1.html')

@app.route('/api/user/<nickname>/followed/')
def followed(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    followed_people = []
    for u in user.followed:
        if u.nickname != nickname:
            followed_people.append(u.user_to_json())
    return jsonify({"followed": followed_people})

@app.route('/lab/spritz')
@app.route('/lab/spritz/<language>')
def spritz(language="chinese"):
    if language == 'english':
        f = open('./app/static/file/article_eg.txt','r')
        article = f.read()
        f.close()
        paragraghs = article.split("\n")
        words = []
        for para in paragraghs:
            words.extend(para.split(' '))
        return render_template('spritz.html', paragraghs=paragraghs, words=words, length=len(words), version='en' )
    if language == 'chinese':
        f = open('./app/static/file/article_ch.txt','r')
        article = f.read()
        f.close()
        article = article.decode('utf-8')
        paragraghs = article.split("\n")
        re_attach_article = ""
        for p in paragraghs:
            re_attach_article += p
        words = jieba.lcut(re_attach_article)
        return render_template('spritz.html', paragraghs=paragraghs, words=words, length=len(words), version='ch' )
    if language == 'chinese_led':
        f = open('./app/static/file/article_ch.txt','r')
        article = f.read()
        f.close()
        clean_article = article.replace(' ','')
        clean_article = clean_article.replace('\n', '')
        clean_article = clean_article.decode('utf-8')
        article = article.decode('utf-8')
        paragraghs = article.split("\n")
        words = list(clean_article)
        return render_template('spritz.html', paragraghs=paragraghs, words=words, length=len(words), version='led')

@app.route('/writing', methods=['GET', 'POST'])
@login_required
def writing():
    user = g.user
    form = EssayForm()
    if form.validate_on_submit():
        time = datetime.utcnow()
        essay = Essay(body=form.essay.data, title=form.title.data,timestamp=time, author=user)
        db.session.add(essay)
        db.session.commit()
        post = Post(
            body = u"发表了一篇文章---<a href='%s'>%s</a>"%(url_for('essay_title', title=form.title.data), form.title.data),
            timestamp = time,
            author = user
            )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("writing.html", form=form, user=user)

@app.route('/essay/<int:id>')
def essay(id):
    essay = Essay.query.get_or_404(id)
    return render_template('essay.html', essay=essay)

@app.route('/essay/title/<title>')
def essay_title(title):
    essay = Essay.query.filter_by(title=title).first()
    return render_template('essay.html', essay=essay)

@app.route('/essays/<nickname>')
def essays(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    essays = user.essays.order_by(Essay.timestamp.desc())
    return render_template('essays.html', essays=essays)

@app.route('/connections/<nickname>')
def connections(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    return render_template('connections.html', user=user)


