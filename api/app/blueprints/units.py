from app import db
from app.models import Unit
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

bp = Blueprint('Units', __name__, url_prefix='/units')


@bp.route('paginated', methods=['GET'])
def get_all_paginated():
    pagination_object = Unit.query.order_by(Unit.name).paginate(
        page=int(request.args.get('page', 1)),
        per_page=int(request.args.get('per_page', 5))
    )

    items = pagination_object.items

    return jsonify({
        'page': pagination_object.page,
        'per_page': pagination_object.per_page,
        'pages': pagination_object.pages,
        'units': [unit.to_dict() for unit in items]
    }), 200


@bp.route('', methods=['GET'])
def get_units():
    return jsonify([unit.to_dict() for unit in Unit.query.order_by(Unit.name).all()]), 200


@bp.route('', methods=['POST'])
def create_unit():
    data = request.get_json()
    if data is None:
        return jsonify('dados vazios'), 500

    errors = {'name': None, 'abbreviation': None}
    name = data.get('name', None)
    abbreviation = data.get('abbreviation', None)

    if name is None:
        errors['name'] = 'Nome é obrigatório'
    if abbreviation is None:
        errors['abbreviation'] = 'Abreviatura é obrigatória'

    if errors['name'] is not None or errors['abbreviation'] is not None:
        return jsonify(errors), 400

    unit = Unit()
    try:
        unit.name = name
        unit.abbreviation = abbreviation
        db.session.add(unit)
        db.session.commit()

    except ValueError as e:
        db.session.rollback()
        err = str(e).lower()
        if 'nome' in err:
            errors['name'] = str(e)
        else:
            errors['abbreviation'] = str(e)

    except IntegrityError as e:
        db.session.rollback()
        if "'units.name'" in str(e):
            errors['name'] = 'Nome já existe'
        else:
            errors['abbreviation'] = 'Abreviatura já existe'

    finally:
        if errors['name'] is not None or errors['abbreviation'] is not None:
            return jsonify(errors), 400
        return jsonify(unit.to_dict()), 201


@bp.route('unit/<unit_id>', methods=['GET'])
def get_unit_by_id(unit_id):
    unit = Unit.query.filter_by(id=unit_id).first()
    if unit is None:
        return jsonify('Unidade não encontrada'), 404

    return jsonify(unit.to_dict()), 200


@bp.route('unit/<unit_id>', methods=['PATCH', 'PUT'])
def update_unit(unit_id):
    unit = Unit.query.filter_by(id=unit_id).first()
    if unit is None:
        return jsonify('unidade não encontrada'), 404

    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 500
    errors = {'name': None, 'abbreviation': None}

    try:
        name = data.get('name', None)
        if name is not None and unit.name != name:
            unit.name = name

        abbreviation = data.get('abbreviation', None)
        if abbreviation is not None and unit.abbreviation != abbreviation:
            unit.abbreviation = abbreviation
        db.session.commit()

    except ValueError as e:
        db.session.rollback()
        err = str(e).lower()
        if 'nome' in err:
            errors['name'] = str(e)
        else:
            errors['abbreviation'] = str(e)

    except IntegrityError as e:
        db.session.rollback()
        if "'units.name'" in str(e):
            errors['name'] = 'Nome já existe'
        else:
            errors['abbreviation'] = 'Abreviatura já existe'
    finally:
        if errors['name'] is not None or errors['abbreviation'] is not None:
            return jsonify(errors), 400
        return jsonify(unit.to_dict()), 200


@bp.route('unit/<unit_id>', methods=['DELETE'])
def delete_unit(unit_id):
    unit = Unit.query.filter_by(id=unit_id).first()
    if unit is None:
        return jsonify('Unidade não encontrada'), 404

    db.session.delete(unit)
    try:
        db.session.commit()
        return jsonify('Unidade apagada'), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify('Impossível apagar unidade usada em material, produto ou produção.'), 400
