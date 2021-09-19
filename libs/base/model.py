import datetime

import uuid

from flask_sqlalchemy import BaseQuery
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID

from nft.ext import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(UUID, default=lambda: str(uuid.uuid4()), primary_key=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.now,
                           index=True)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        index=True,
    )

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter(cls.id == _id).first()

    @classmethod
    def find_by_ids(cls, _ids):
        if not _ids:
            return []
        return cls.query.filter(cls.id.in_(_ids)).all()

    @classmethod
    def add(cls, **kwargs):
        auto_commit = kwargs.pop("auto_commit", True)
        obj = cls(**kwargs)
        db.session.add(obj)
        try:
            if auto_commit:
                db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise

        return obj

    @classmethod
    def get_count(cls, q):
        count_q = q.statement.with_only_columns([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count

    def delete(self, auto_commit=True):
        db.session.delete(self)
        if auto_commit:
            db.session.commit()

    def to_json(self):
        return {c.key: getattr(self, c.key, None)
                for c in self.__class__.__table__.columns}
