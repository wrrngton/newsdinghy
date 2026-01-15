from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app
from app.utils import is_url_rss


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Jez'}
    return render_template('index.html', title='Home', user=user)


@app.route('/settings')
def settings():
    return render_template('settings.html', title='Settings')


@app.route('/submit', methods=['POST'])
def handle_form():
    url = request.form.get("url")

    if not url:
        flash('url could not be parsed, or is not an RSS feed')
        return jsonify({"error": "Missing url field"}), 400

    is_rss, message = is_url_rss(url)

    if not is_rss:
        flash(message)
        return redirect(url_for('settings'))

    flash('Rss feed successfully added')

    return redirect(url_for('settings'))
