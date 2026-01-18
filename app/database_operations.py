from app import db
from app.models import User, Feed, Article, user_feeds
from app.errors import DatabaseError, ResourceNotFoundError, DataValidationError
from flask_login import current_user
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


def get_user_feeds(user: int) -> list:
    feeds_query = current_user.feeds.select()
    user_feeds = db.session.scalars(feeds_query).all()
    return user_feeds


def get_user_articles(user: int) -> list:
    try:
        user_feeds = get_user_feeds(user)
        user_feed_ids = [u.id for u in user_feeds]
        user_articles = db.session.scalars(sa.select(Article).filter(
            Article.feed_id.in_(user_feed_ids))).all()
    except SQLAlchemyError as e:
        print(e)
        raise DatabaseError('Error fetching articles from database')
    return user_articles


# def get_user_feeds_urls(user: int) -> list:
#     user_feed_urls = db.session.execute(sa.select(Feed.url).where(Feed.user_id == user)).all()
#     return user_feed_urls


def delete_user_feed(feed_id: int):
    try:
        feed_to_remove = db.session.get(Feed, feed_id)
        current_user.feeds.remove(feed_to_remove)

        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise DataValidationError(
            "The requested resouces to delete have an error.")
    except SQLAlchemyError as e:
        print(e)
        db.session.rollback()
        raise DatabaseError(
            "A technical error occurred while deleting from the database")


def add_user_feed(feed: dict):
    url = feed.get('url')
    db_feed = db.session.scalar(sa.select(Feed).where(Feed.url == url))

    if not db_feed:
        db_feed = Feed(url=feed.get('url'), author=feed.get(
            'author'), description=feed.get('description'), website=feed.get('website'))
        db.session.add(db_feed)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            db_feed = db.session.scalar(sa.select(Feed).where(Feed.url == url))

    is_subscribed = db.session.scalar(
        sa.select(user_feeds).where(
            user_feeds.c.user_id == current_user.id,
            user_feeds.c.feed_id == db_feed.id
        )
    )

    if is_subscribed:
        raise DataValidationError('You are already subscribed to this feed')

    current_user.feeds.add(db_feed)
    db.session.commit()


def index_feed_articles(articles_json: list[dict], url: str):
    try:
        feed_id = db.session.execute(sa.Select(Feed.id).where(
            Feed.url == url)).scalar_one_or_none()

        if feed_id is None:
            raise ResourceNotFoundError(f"No feed found with URL: {url}")

        article_objects = [Article(url=a.get('url'), title=a.get(
            'title'), timestamp=a.get('timestamp'), feed_id=feed_id) for a in articles_json]
        db.session.add_all(article_objects)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise DataValidationError(
            "One of more articles already exist or have invalid data.")
    except SQLAlchemyError as e:
        print(e, "egg2")
        db.session.rollback()
        raise DatabaseError(
            "A technical error occurred while saving to the database")
