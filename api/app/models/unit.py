from app import db
from sqlalchemy.orm import validates
from uuid import uuid4


class Unit(db.Model):
    __tablename__ = 'units'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(240), nullable=False, unique=True)
    abbreviation = db.Column(db.String(20), nullable=False, unique=True)

    @validates('name')
    def validates_name(self, key, value):
        if (3 <= len(value) <= 240) is False:
            raise ValueError('Nome deve ter entre 3 e 240 caracteres')
        return value

    @validates('abbreviation')
    def validates_abbreviation(self, key, value):
        if (1 <= len(value) <= 20) is False:
            raise ValueError('Abreviatura deve ter entre 1 e 20 caracteres')
        return value

    def __repr__(self):
        return f'<Unit {self.name} ({self.abbreviation})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
        }
