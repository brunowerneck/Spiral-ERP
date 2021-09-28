from app import db
from app.models import Material, Product
from app.validators import validate_name
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

bp = Blueprint('Products', __name__, url_prefix='/products')


@bp.route('', methods=['GET'])
def get_products():
    return jsonify([product.to_dict() for product in Product.query.order_by(Product.name).all()]), 200


@bp.route('', methods=['POST'])
def create_product():
    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 400

    name = data.get('name', None)
    if name is None:
        return jsonify(['Nome é obrigatório']), 400

    if validate_name(name) is False:
        return jsonify(['Nome deve ter entre 3 e 240 caracteres']), 400

    product = Product(
        name=name,
        short_description=data.get('short_description', None),
        long_description=data.get('long_description', None)
    )

    for material in data.get('materials', []):
        mat = Material.query.filter_by(id=material['id']).first()
        product.materials.append(mat)

    db.session.add(product)
    try:
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify([f'O produto {name} já existe em nossos registros']), 400


@bp.route('product/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return jsonify('Produto não encontrado'), 404

    return jsonify(product.to_dict()), 200


@bp.route('product/<product_id>', methods=['PATCH', 'PUT'])
def update_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return jsonify('Produto não encontrado'), 404

    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 400
    try:
        if 'name' in data:
            name = data.get('name')
            if name is None:
                return jsonify(['Nome é obrigatório']), 400

            if validate_name(name) is False:
                return jsonify(['Nome deve ter entre 3 e 240 caracteres']), 400
            # else
            if product.name != name:
                product.name = name

        if 'short_description' in data and product.short_description != data.get('short_description'):
            product.short_description = data.get('short_description')

        if 'long_description' in data and product.long_description != data.get('long_description'):
            product.long_description = data.get('long_description')

        if 'materials' in data:
            product.materials.clear()
            for mat in data['materials']:
                material = Material.query.filter_by(id=mat['id']).first()

                if material is None:
                    return jsonify('Material não encontrado'), 404
                # else
                product.materials.append(material)

        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify([f'O produto {name} já existe em nossos registros.']), 400

    return jsonify(product.to_dict()), 200


@bp.route('product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return jsonify('Produto não encontrado'), 404

    db.session.delete(product)
    try:
        db.session.commit()
        return jsonify('Produto apagado'), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify('Impossível apagar produto usado em Produção.'), 400
