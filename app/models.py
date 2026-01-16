from typing import Optional
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    feeds: so.WriteOnlyMapped['Feed'] = so.relationship(
        back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Feed(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    url: so.Mapped[str] = so.mapped_column(sa.String(64))
    author: so.Mapped[str] = so.mapped_column(sa.String(64))
    website: so.Mapped[str] = so.mapped_column(sa.String(64))
    description: so.Mapped[str] = so.mapped_column(sa.String(120))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True)
    user: so.Mapped[User] = so.relationship(back_populates='feeds')
    articles: so.WriteOnlyMapped['Article'] = so.relationship(
        back_populates='feed')

    def __repr__(self):
        return '<Feed {}>'.format(self.url)


class Article(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    url: so.Mapped[str] = so.mapped_column(sa.String(64))
    title: so.Mapped[str] = so.mapped_column(sa.String(64))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True)
    feed_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Feed.id), index=True)
    feed: so.Mapped[Feed] = so.relationship(back_populates='articles')

    def __repr__(self):
        return '<Article {}>'.format(self.title)
