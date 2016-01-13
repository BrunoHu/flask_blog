#!/flask/bin/python
#coding:utf-8

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
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

    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
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
def spritz():
    paragraghs =[
    '''Dear Max,''',
    '''Your mother and I don't yet have the words to describe the hope you give us for the future. Your new life is full of promise, and we hope you will be happy and healthy so you can explore it fully. You've already given us a reason to reflect on the world we hope you live in. Like all parents, we want you to grow up in a world better than ours today.''',
    '''While headlines often focus on what's wrong, in many ways the world is getting better. Health is improving. Poverty is shrinking. Knowledge is growing. People are connecting. Technological progress in every field means your life should be dramatically better than ours today.''',
    '''We will do our part to make this happen, not only because we love you, but also because we have a moral responsibility to all children in the next generation.''',
    '''We believe all lives have equal value, and that includes the many more people who will live in future generations than live today. Our society has an obligation to invest now to improve the lives of all those coming into this world, not just those already here.''',
    '''But right now, we don't always collectively direct our resources at the biggest opportunities and problems your generation will face.''',
    '''Consider disease. Today we spend about 50 times more as a society treating people who are sick than we invest in research so you won't get sick in the first place.''',
    '''Medicine has only been a real science for less than 100 years, and we've already seen complete cures for some diseases and good progress for others. As technology accelerates, we have a real shot at preventing, curing or managing all or most of the rest in the next 100 years.''',
    '''Today, most people die from five things -- heart disease, cancer, stroke, neurodegenerative and infectious diseases -- and we can make faster progress on these and other problems.''',
    '''Once we recognize that your generation and your children's generation may not have to suffer from disease, we collectively have a responsibility to tilt our investments a bit more towards the future to Facebook.A letter to our daughtermake this reality. Your mother and I want to do our part.''',
    '''Curing disease will take time. Over short periods of five or ten years, it may not seem like we're making much of a difference. But over the long term, seeds planted now will grow, and one day, you or your children will see what we can only imagine: a world without suffering from disease.''',
    '''There are so many opportunities just like this. If society focuses more of its energy on these great challenges, we will leave your generation a much better world.''',
    '''Our hopes for your generation focus on two ideas: advancing human potential and promoting equality.''',
    '''Advancing human potential is about pushing the boundaries on how great a human life can be.''',
    '''Can you learn and experience 100 times more than we do today?''',
    '''Can our generation cure disease so you live much longer and healthier lives?''',
    '''Can we connect the world so you have access to every idea, person and opportunity?''',
    '''Can we harness more clean energy so you can invent things we can't conceive of today while protecting the environment?''',
    '''Can we cultivate entrepreneurship so you can build any business and solve any challenge to grow peace and prosperity?''',
    '''Promoting equality is about making sure everyone has access to these opportunities -- regardless of the nation, families or circumstances they are born into.''',
    '''Our society must do this not only for justice or charity, but for the greatness of human progress.''',
    '''Today we are robbed of the potential so many have to offer. The only way to achieve our full potential is to channel the talents, ideas and contributions of every person in the world.''',
    '''Can our generation eliminate poverty and hunger?''',
    '''Can we provide everyone with basic healthcare?''',
    '''Can we build inclusive and welcoming communities?''',
    '''Can we nurture peaceful and understanding relationships between people of all nations?''',
    '''Can we truly empower everyone -- women, children, underrepresented minorities, immigrants and the unconnected?''']
    article = ' '.join(paragraghs)
    words = article.split(" ")
    for i in range(len(words)):
        words[i] = words[i].strip(' \n')
    return render_template('spritz.html', paragraghs=paragraghs, words=words, length=len(words) )
