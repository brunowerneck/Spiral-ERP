from app import db
from sqlalchemy.orm import validates
from uuid import uuid4


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(240), nullable=False, unique=True)

    @validates('name')
    def validate_name(self, key, value):
        if (3 <= len(value) <= 240) is False:
            raise ValueError('Nome deve ter entre 3 e 240 caracteres')
        return value

    def __repr__(self):
        return f'<Supplier {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
