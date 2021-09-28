from app import db
from sqlalchemy.orm import validates
from uuid import uuid4


class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(240), nullable=False)
    unit_value = db.Column(db.Float, nullable=False, default=0)

    supplier_id = db.Column(db.String(36), db.ForeignKey('suppliers.id'), nullable=False)
    supplier = db.relationship('Supplier', backref='materials')

    unit_id = db.Column(db.String(36), db.ForeignKey('units.id'), nullable=False)
    unit = db.relationship('Unit')

    @validates('name')
    def validates_name(self, key, value):
        materials = Material.query.filter_by(supplier_id=self.supplier_id).all()
        for mat in materials:
            if mat.name == value:
                raise ValueError(f'O fornecedor {mat.supplier.name} já tem o material {value} cadastrado')

        if (3 <= len(value) <= 240) is False:
            raise ValueError('Nome deve ter entre 3 e 240 caracteres')
        return value

    def __repr__(self):
        return f'<Material {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'unit_value': self.unit_value,
            'unit': self.unit.to_dict() if self.unit_id is not None else {},
            'supplier': self.supplier.to_dict()
        }
