from app import db
from app.models import User, Feed
from flask_login import current_user
import sqlalchemy as sa

def get_user_feeds(user: int) -> list:
    user_feeds = db.session.execute(sa.select(Feed.url, Feed.author).where(Feed.user_id == user)).all()
    return user_feeds

# def get_user_feeds_urls(user: int) -> list:
#     user_feed_urls = db.session.execute(sa.select(Feed.url).where(Feed.user_id == user)).all()
#     return user_feed_urls

def index_feed_articles():
    pass

