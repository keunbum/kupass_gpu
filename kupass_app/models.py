from kupass_app import db
from sqlalchemy.dialects.mysql import LONGTEXT

article_keyword = db.Table(
    'article_keyword',
    db.Column('article_id', db.BigInteger, db.ForeignKey('article.id', ondelete='CASCADE'), primary_key=True),
    db.Column('keyword_id', db.BigInteger, db.ForeignKey('keyword.id', ondelete='CASCADE'), primary_key=True),
)

user_keyword = db.Table(
    'user_keyword',
    db.Column('user_id', db.BigInteger, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('keyword_id', db.BigInteger, db.ForeignKey('keyword.id', ondelete='CASCADE'), primary_key=True),
)


class Article(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(LONGTEXT, nullable=False)
    summary = db.Column(db.String(1023), nullable=True)
    category = db.Column(db.String(255), nullable=True)
    publisher = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(255), nullable=True)
    create_date = db.Column(db.DateTime(6), nullable=False)
    keyword = db.relationship('Keyword', secondary=article_keyword, backref=db.backref('article_keyword_set'))


class Keyword(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False, index=True, unique=True)


class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    activated = db.Column(db.Boolean, nullable=True)
    nickname = db.Column(db.String(255), nullable=True)
    keyword = db.relationship('Keyword', secondary=user_keyword, backref=db.backref('user_keyword_set'))
