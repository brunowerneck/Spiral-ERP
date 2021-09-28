from app import db
from app.models import Material, Supplier, Unit
from app.validators import validate_name
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

bp = Blueprint('Materials', __name__, url_prefix='/materials')


@bp.route('', methods=['GET'])
def get_materials():
    return jsonify([mat.to_dict() for mat in Material.query.order_by(Material.name).all()]), 200


@bp.route('', methods=['POST'])
def create_material():
    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 500
    errors = {
        'name': None,
        'supplier': None,
        'unit': None,
        'unit_value': None
    }

    name = data.get('name', None)
    if name is None:
        errors.update({'name': 'Nome é obrigatório'})
    supplier = data.get('supplier', [])
    if len(supplier) == 0:
        errors.update({'supplier': 'Fornecedor é obrigatório'})
    unit = data.get('unit', [])
    if len(unit) == 0:
        errors.update({'unit': 'Unidade é obrigatória'})
    unit_value = data.get('unit_value', 0)
    if unit_value == '' or float(unit_value) <= 0:
        errors.update({'unit_value': 'O valor unitário deve ser maior que zero'})
    if errors['name'] is not None \
            or errors['supplier'] is not None \
            or errors['unit'] is not None \
            or errors['unit_value'] is not None:
        return jsonify(errors), 400

    supplier_id = supplier.get('id')
    unit_id = unit.get('id')
    material = Material()
    try:
        material.supplier_id = supplier_id
        material.name = name
        material.unit_id = unit_id
        material.unit_value = unit_value
        db.session.add(material)
        db.session.commit()

    except ValueError as e:
        db.session.rollback()
        err = str(e).lower()
        if 'nome' in err:
            errors.update({'name': str(e)})
        if 'fornecedor' in err:
            errors.update({'supplier': str(e)})
        if 'unidade' in err:
            errors.update({'unit': str(e)})
        if 'valor unitário' in err:
            errors.update({'unit_value': str(e)})

    except IntegrityError:
        db.session.rollback()
        errors.update({'name': f'O material {name} já existe em nossos registros'})

    finally:
        if errors['name'] is not None \
                or errors['supplier'] is not None \
                or errors['unit'] is not None \
                or errors['unit_value'] is not None:
            return jsonify(errors), 400

        return jsonify(material.to_dict()), 201


@bp.route('material/<material_id>', methods=['GET'])
def get_material_by_id(material_id):
    mat = Material.query.filter_by(id=material_id).first()
    if mat is None:
        return jsonify('Material não encontrado'), 404

    return jsonify(mat.to_dict()), 200


@bp.route('material/<material_id>', methods=['PATCH', 'PUT'])
def update_material(material_id):
    mat = Material.query.filter_by(id=material_id).first()
    if mat is None:
        return jsonify('Material não encontrado'), 404

    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 500

    errors = {
        'name': None,
        'supplier': None,
        'unit': None,
        'unit_value': None
    }

    try:
        if 'supplier' in data:
            supplier_id = data.get('supplier').get('id')
            # else
            if supplier_id != mat.supplier_id:
                materials = Material.query.filter_by(supplier_id=supplier_id).all()
                for _ in materials:
                    if _.name == mat.name:
                        raise ValueError(f'O fornecedor {mat.supplier.name} já tem o material {mat.name} cadastrado')
                mat.supplier_id = supplier_id

        if 'name' in data:
            new_name = data.get('name')
            if validate_name(new_name) is False:
                raise ValueError('Nome deve ter entre 3 e 240 caracteres')
            # else
            if mat.name != new_name:
                mat.name = new_name

        if 'unit' in data:
            unit_id = data['unit']['id']
            if mat.unit_id != unit_id:
                mat.unit_id = unit_id

        if 'unit_value' in data:
            unit_value = data.get('unit_value')
            if unit_value == '' or float(unit_value) <= 0.0:
                raise ValueError('O valor unitário deve ser maior que zero')
            # else
            if mat.unit_value != unit_value:
                mat.unit_value = unit_value

        db.session.commit()

    except ValueError as e:
        db.session.rollback()
        err = str(e).lower()
        if 'nome' in err:
            errors.update({'name': str(e)})
        if 'fornecedor' in err:
            errors.update({'supplier': str(e)})
        if 'unidade' in err:
            errors.update({'unit': str(e)})
        if 'valor unitário' in err:
            errors.update({'unit_value': str(e)})

    except IntegrityError:
        db.session.rollback()
        errors.update({'name': f'O material {mat.name} já existe em nossos registros'})

    finally:
        if errors['name'] is not None \
                or errors['supplier'] is not None \
                or errors['unit'] is not None \
                or errors['unit_value'] is not None:
            return jsonify(errors), 400

        return jsonify(mat.to_dict()), 200


@bp.route('material/<material_id>', methods=['DELETE'])
def delete_material(material_id):
    mat = Material.query.filter_by(id=material_id).first()
    if mat is None:
        return jsonify('Material não encontrado'), 404

    db.session.delete(mat)
    try:
        db.session.commit()
        return jsonify('Material apagado'), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify('Impossível apagar material usado em Produção.'), 400
