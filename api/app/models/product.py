from app import db
from sqlalchemy.dialects.mysql import INTEGER
from uuid import uuid4


product_materials = db.Table(
    'product_materials',
    db.Column('id', INTEGER(unsigned=True), primary_key=True, autoincrement=True),
    db.Column('product_id', db.String(36), db.ForeignKey('products.id'), primary_key=True),
    db.Column('material_id', db.String(36), db.ForeignKey('materials.id'), primary_key=True),
)


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(240), nullable=False, unique=True)
    short_description = db.Column(db.String(240), nullable=True)
    long_description = db.Column(db.Text, nullable=True)
    materials = db.relationship(
        'Material',
        secondary=product_materials,
        lazy='subquery',
        backref=db.backref('products', lazy=True)
    )

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'short_description': self.short_description,
            'long_description': self.long_description,
            'materials': [mat.to_dict() for mat in self.materials]
        }
