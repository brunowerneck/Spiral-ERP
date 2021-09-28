from app import db
from datetime import datetime
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import validates
from uuid import uuid4


class Status(db.Model):
    __tablename__ = 'statuses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(240), nullable=False, unique=True)
    order = db.Column(TINYINT(2, unsigned=True), nullable=False, unique=True)

    @validates('name')
    def validates_name(self, key, value: str):
        if (2 <= len(value) <= 240) is False:
            raise ValueError('Nome deve ter entre 3 e 240 caracteres')
        return value.upper()

    def __repr__(self):
        return f'<Status {self.order}:{self.name}>'

    def __gt__(self, other):
        return self.order > other.order

    def __lt__(self, other):
        return self.order < other.order

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'order': self.order,
        }


class BatchMaterial(db.Model):
    __tablename__ = 'batch_materials'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    batch_id = db.Column(db.String(36), db.ForeignKey('batches.id'), primary_key=True)

    material_id = db.Column(db.String(36), db.ForeignKey('materials.id'), primary_key=True)
    material = db.relationship('Material')

    amount = db.Column(db.Float, nullable=False, default=0)
    unit_value = db.Column(db.Float, nullable=False, default=0)

    def __repr__(self):
        return f'<BM {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'material': self.material.to_dict(),
            'amount': self.amount,
            'unit_value': self.unit_value
        }


class BatchStatus(db.Model):
    __tablename__ = 'batch_statuses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    batch_id = db.Column(db.String(36), db.ForeignKey('batches.id'), primary_key=True)

    status_id = db.Column(db.String(36), db.ForeignKey('statuses.id'), primary_key=True)
    status = db.relationship(Status)

    notes = db.Column(db.Text)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f'<BatchStatus {self.status.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status.to_dict(),
            'notes': self.notes,
            'created': self.created
        }


class Batch(db.Model):
    __tablename__ = 'batches'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))

    product_id = db.Column(db.String(36), db.ForeignKey('products.id'))
    product = db.relationship('Product')

    materials = db.relationship(BatchMaterial, cascade='all, delete-orphan')
    statuses = db.relationship(BatchStatus, cascade='all, delete-orphan', order_by=BatchStatus.created.desc)

    output = db.Column(db.Float, nullable=False, default=1)
    output_unit_id = db.Column(db.String(36), db.ForeignKey('units.id'))
    output_unit = db.relationship('Unit')

    unit_value = db.Column(db.Float, nullable=False, default=0)

    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.now)

    def __repr__(self):
        return f'<Batch {self.product.name} {self.created.date()}>'

    def get_current_unit_value(self):
        return self.get_total_cost() / float(self.output)

    def get_total_cost(self):
        value = 0
        for bm in self.materials:
            value += float(bm.unit_value) * float(bm.amount)
        return value

    def calculate_unit_value(self):
        self.unit_value = self.get_current_unit_value()

    def to_dict(self):
        return {
            'id': self.id,
            'number': str(self.created.timestamp()).replace('.', ''),
            'product': self.product.name,
            'output': self.output,
            'output_unit': self.output_unit.to_dict() if self.output_unit_id else {},
            'total_cost': self.get_total_cost(),
            'unit_value': self.unit_value,
            'materials': [bm.to_dict() for bm in self.materials],
            'statuses': [bs.to_dict() for bs in self.statuses],
            'status': self.statuses[0].to_dict(),
            'created': self.created,
            'updated': self.updated,
        }
