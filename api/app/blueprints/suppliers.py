from app import db
from app.models import Material, Supplier
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, OperationalError

bp = Blueprint('Suppliers', __name__, url_prefix='/suppliers')


@bp.route('', methods=['GET'])
def get_suppliers():
    sups = [supplier.to_dict() for supplier in Supplier.query.order_by(Supplier.name).all()]
    for sup in sups:
        sup.update({'materials': Material.query.filter_by(supplier_id=sup.get('id')).count()})
    return jsonify(sups), 200


@bp.route('', methods=['POST'])
def create_supplier():
    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 500

    errors = {'name': None}
    name = data.get('name', None)

    if name is None:
        errors['name'] = 'Nome é obrigatório'
        return jsonify(errors), 400

    supplier = Supplier()
    try:
        supplier.name = name
        db.session.add(supplier)
        db.session.commit()

    except ValueError as e:
        db.session.rollback()
        errors['name'] = str(e)

    except IntegrityError:
        db.session.rollback()
        errors['name'] = f'O fornecedor com nome {name} já existe em nossos registros'

    finally:
        if errors['name'] is not None:
            return jsonify(errors), 400
        return jsonify(supplier.to_dict()), 201


@bp.route('supplier/<supplier_id>', methods=['GET'])
def get_supplier_by_id(supplier_id):
    supplier = Supplier.query.filter_by(id=supplier_id).first()
    if supplier is None:
        return jsonify('Fornecedor não encontrado'), 404

    return jsonify(supplier.to_dict()), 200


@bp.route('supplier/<supplier_id>/materials', methods=['GET'])
def get_supplier_materials(supplier_id):
    supplier = Supplier.query.filter_by(id=supplier_id).first()
    if supplier is None:
        return jsonify('Fornecedor não encontrado'), 404

    return jsonify([mat.to_dict() for mat in supplier.materials]), 200


@bp.route('supplier/<supplier_id>', methods=['PATCH', 'PUT'])
def update_supplier(supplier_id):
    supplier = Supplier.query.filter_by(id=supplier_id).first()
    if supplier is None:
        return jsonify({'name': 'Fornecedor não encontrado'}), 404

    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 500

    errors = {'name': None}
    try:
        name = data.get('name', None)
        if name is not None and supplier.name != name:
            supplier.name = name
        db.session.commit()

    except ValueError as e:
        db.session.rollback()
        errors['name'] = str(e)

    except IntegrityError:
        db.session.rollback()
        errors['name'] = f'O fornecedor com nome {name} já existe em nossos registros'

    finally:
        if errors['name'] is not None:
            return jsonify(errors), 400
        return jsonify(supplier.to_dict()), 200


@bp.route('supplier/<supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    supplier = Supplier.query.filter_by(id=supplier_id).first()
    if supplier is None:
        return jsonify('Fornecedor não encontrado'), 404

    db.session.delete(supplier)

    try:
        db.session.commit()
        return jsonify('Fornecedor apagado'), 200
    except (IntegrityError, OperationalError):
        db.session.rollback()
        return jsonify('Impossível apagar fornecedor. Apague primeiro os materiais.'), 400
