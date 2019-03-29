from ..app import db
from ._pv_module import PvModule


class Measurement(db.Model):
    __tablename__ = __qualname__

    id = db.Column(db.Integer, primary_key=True)
    fk_pv_module = db.Column(db.Integer, db.ForeignKey('PvModule.id'), nullable=False)
    pv_module = db.relationship('PvModule',
                                      backref=db.backref('measurements', lazy=True))

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
