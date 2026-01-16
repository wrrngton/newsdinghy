from app import db
from app.models import User, Feed
import sqlalchemy as sa

def get_user_feeds(user: int) -> list:
    user_feeds = db.session.execute(sa.select(Feed.url, Feed.author).where(Feed.user_id == user)).all()
    return user_feeds


