from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.utils import is_url_rss, get_feed_info, generate_soup, process_feed_articles
from app.database_operations import get_user_feeds, index_feed_articles, delete_user_feed, add_user_feed, get_user_articles, get_single_feed_articles, get_single_user_feed, get_single_feed_article_count
from app.models import Feed, User
from app.errors import DatabaseError, DataValidationError
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError


@app.route('/')
@app.route('/index')
@login_required
def index():
    user_feeds = get_user_feeds(current_user.id)
    for uf in user_feeds:
        uf.count = get_single_feed_article_count(uf.id)
    return render_template('index.html', title='Home', user=current_user, user_feeds=user_feeds)


@app.route('/feeds')
@login_required
def feeds():
    user_feeds = get_user_feeds(current_user.id)
    return render_template('feeds.html', title='Settings', user_feeds=user_feeds)


@app.route('/feeds/<feed_id>', methods=['GET'])
@login_required
def single_feed(feed_id):
    single_feed_articles = False
    try:
        single_feed_articles = get_single_feed_articles(
            feed_id, current_user.id)
        single_feed_info = get_single_user_feed(current_user.id, feed_id)
        return render_template('single_feed.html', single_feed_articles=single_feed_articles, single_feed_info=single_feed_info)
    except DataValidationError as e:
        flash(str(e))
        return redirect(url_for('feeds'))
    except DatabaseError as e:
        flash(str(e))
        return redirect(url_for('feeds'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('login.html', title="Login")

    submitted_username = request.form.get('username')
    submitted_password = request.form.get('password')
    submitted_remember_me = True if request.form.get('remember-me') else False

    if request.method != "POST" or submitted_username == "" or submitted_password == "":
        flash('Username or password not entered')
        return redirect(url_for('login'))

    user = db.session.scalar(sa.select(User).where(
        User.username == submitted_username))
    if user is None or not user.check_password(submitted_password):
        print('doing this')
        flash('Invalid username or password')
        return redirect(url_for('login'))
    login_user(user, remember=submitted_remember_me)
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/submit', methods=['POST'])
def handle_form():
    url = request.form.get("url")

    if not url:
        flash('please provide a URL')
        return redirect(url_for('feeds'))

    soup, message = generate_soup(url)

    if not soup:
        flash(message)
        return redirect(url_for('feeds'))

    is_rss, message = is_url_rss(soup)

    if not is_rss:
        flash(message)
        return redirect(url_for('feeds'))

    feed = get_feed_info(soup)

    try:
        add_user_feed(feed)
        flash('Feed successfully added')
    except DatabaseError as e:
        flash(str(e))
    except DataValidationError as e:
        flash(str(e))

    articles_json, message = process_feed_articles(url)

    if not articles_json:
        flash(message)

    try:
        index_feed_articles(articles_json, url)
        flash('Articles successfully indexed')
    except DatabaseError as e:
        flash(str(e))
    except DataValidationError as e:
        flash(str(e))

    return redirect(url_for('feeds'))


@app.route('/delete-feed', methods=['POST'])
def delete_feed():
    try:
        feed_id = request.form.get('feed-id')
        delete_user_feed(feed_id)
    except DatabaseError as e:
        flash(e)
    except DataValidationError as e:
        flash(e)
    return redirect(url_for('feeds'))
