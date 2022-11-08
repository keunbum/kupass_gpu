from kupass_app import db
from sqlalchemy.dialects.mysql import LONGTEXT

article_keywords = db.Table(
    'article_keywords',
    db.Column('article_keyword_id', db.BigInteger, primary_key=True),
    db.Column('article_id', db.BigInteger, db.ForeignKey('article.article_id', ondelete='CASCADE'), nullable=False),
    db.Column('keyword_id', db.BigInteger, db.ForeignKey('keyword.keyword_id', ondelete='CASCADE'), nullable=False),
)

interesting_keyword = db.Table(
    'interesting_keyword',
    db.Column('interesting_keyword_id', db.BigInteger, primary_key=True),
    db.Column('user_id', db.BigInteger, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False),
    db.Column('keyword_id', db.BigInteger, db.ForeignKey('keyword.keyword_id', ondelete='CASCADE'), nullable=False),
)


class Article(db.Model):
    article_id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(LONGTEXT, nullable=False)
    summary = db.Column(LONGTEXT, nullable=True)
    category = db.Column(db.String(255), index=True, nullable=True)
    publisher = db.Column(db.String(255), index=True, nullable=True)
    source = db.Column(db.String(255), index=True, unique=True, nullable=True)
    create_date = db.Column(db.DateTime(6), index=True, nullable=False)
    keyword = db.relationship('Keyword', secondary=article_keywords, backref=db.backref('article_keyword_set'))


class Keyword(db.Model):
    keyword_id = db.Column(db.BigInteger, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False, index=True, unique=True)


class User(db.Model):
    user_id = db.Column(db.BigInteger, primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    activated = db.Column(db.Boolean, nullable=True)
    nickname = db.Column(db.String(255), nullable=True)
    keyword = db.relationship('Keyword', secondary=interesting_keyword, backref=db.backref('user_keyword_set'))
