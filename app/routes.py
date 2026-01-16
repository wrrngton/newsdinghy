from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_user
from app import app, db
from app.utils import is_url_rss, get_feed_info, generate_soup
from app.database_operations import get_user_feeds
from app.models import Feed, User
from sqlalchemy.exc import IntegrityError


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Jez'}
    return render_template('index.html', title='Home', user=user)


@app.route('/feeds')
def feeds():
    user_feeds = get_user_feeds(1)
    return render_template('settings.html', title='Settings', user_feeds=user_feeds)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('login.html', title="Login")

    if request.method != "POST" or request.form.get('username') == "" or request.form.get('password') == "":
        flash('Username or password not entered')
        return redirect(url_for('login'))
    return 'hello world'


@app.route('/submit', methods=['POST'])
def handle_form():
    url = request.form.get("url")

    if not url:
        flash('please provide a URL')
        return jsonify({"error": "Missing url field"}), 400

    soup = generate_soup(url)

    if not soup:
        flash('Could not fetch the URL.')
        return jsonify({"error": "Could not fetch the URL"}), 400

    is_rss, message = is_url_rss(soup)

    if not is_rss:
        flash(message)
        return redirect(url_for('settings'))

    feed = get_feed_info(soup)

    try:
        db_feed = Feed(url=feed.get('url'), user_id=1, author=feed.get(
            'author'), description=feed.get('description'), website=feed.get('website'))

        db.session.add(db_feed)
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()
        flash(f'The following error occurred: {e.orig}')
        return redirect(url_for('settings'))

    except Exception as e:
        db.session.rollback()
        flash(f'The following error occurred: {e.orig}')
        return redirect(url_for('settings'))

    return redirect(url_for('settings'))
