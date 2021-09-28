from app import db
from app.models import Batch, BatchMaterial, BatchStatus, Status, Product, Unit
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, jsonify, request


bp = Blueprint('Batches', __name__, url_prefix='/batches')


@bp.route('', methods=['GET'])
def get_all_batches():
    return jsonify([b.to_dict() for b in Batch.query.order_by(Batch.created).all()]), 200


@bp.route('', methods=['POST'])
def create_batch():
    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 400

    product = Product.query.filter_by(id=data.get('product_id', '')).first()
    if product is None:
        return jsonify('Produto não encontrado'), 404

    output_unit = Unit.query.filter_by(id=data.get('output_unit_id', '')).first()
    if output_unit is None:
        return jsonify(['Unidade de rendimento não encontrada']), 404

    output = data.get('output', 0)
    if output == '' or float(output) <= 0:
        return jsonify(['Rendimento esperado deve ser maior que zero']), 400

    batch = Batch(product_id=product.id, output_unit_id=output_unit.id, output=output)

    for material in data.get('materials'):
        bm = BatchMaterial(material_id=material['id'])
        bm.unit_value = material['unit_value']
        bm.amount = material['amount']
        batch.materials.append(bm)

    batch.calculate_unit_value()
    CRIADO = Status.query.filter_by(name='CRIADO').first()
    if CRIADO is None:
        return jsonify('Status de Produção CRIADO não foi encontrado'), 404
    bs = BatchStatus(status=CRIADO, notes='Produção Criada')
    batch.statuses.append(bs)

    db.session.add(batch)
    db.session.commit()

    return jsonify(batch.to_dict()), 201


@bp.route('batch/<batch_id>', methods=['GET'])
def get_batch_by_id(batch_id):
    batch = Batch.query.filter_by(id=batch_id).first()
    if batch is None:
        return jsonify('produção não encontrada'), 404

    return jsonify(batch.to_dict()), 200


@bp.route('batch/<batch_id>', methods=['PATCH'])
def update_batch(batch_id):
    batch = Batch.query.filter_by(id=batch_id).first()
    if batch is None:
        return jsonify('Produção não encontrada'), 404

    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 500
    try:
        materials = data.get('materials', [])
        for material in materials:
            bm = BatchMaterial(material_id=material['material']['id'])
            bm.unit_value = material['material']['unit_value']
            bm.amount = material['amount']
            batch.materials.append(bm)

        batch.calculate_unit_value()

        status = Status.query.filter_by(id=data.get('status').get('status').get('id')).first()
        bs = BatchStatus(status=status, notes=data.get('status').get('notes', ''))
        batch.statuses.append(bs)

        batch.output = data.get('output', batch.output)
        db.session.commit()
        return jsonify(batch.to_dict()), 200
    except ZeroDivisionError:
        return jsonify('Rendimento deve ser maior que zero.'), 400


@bp.route('batch/<batch_id>', methods=['DELETE'])
def delete_batch(batch_id):
    batch = Batch.query.filter_by(id=batch_id).first()
    if batch is None:
        return jsonify('Produção não encontrada'), 404
    bs = batch.statuses[0]
    if bs.status.order > 0 and bs.status.order != 90:
        return jsonify(f'<strong>Impossível remover produção com status {bs.status.name}</strong><hr/>'
                       f'Só é possivel apagar produções ainda não iniciadas ou canceladas.'), 400

    db.session.delete(batch)
    db.session.commit()

    return jsonify('Produção removida'), 200


@bp.route('status', methods=['GET'])
def get_all_statuses():
    return jsonify([status.to_dict() for status in Status.query.order_by(Status.order).all()]), 200


@bp.route('status', methods=['POST'])
def create_status():
    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 400

    errors = {'name': None, 'order': None}
    name = data.get('name', None)
    order = data.get('order', None)
    if name is None:
        errors['name'] = 'Status é obrigatório'
    if order is None:
        errors['order'] = 'Ordem é obrigatória'

    status = Status()
    try:
        status.name = name
        status.order = order
        db.session.add(status)
        db.session.commit()

    except ValueError as e:
        db.session.rollback()
        err = str(e).lower()
        if 'status' in err:
            errors['name'] = str(e)
        if 'order' in err:
            errors['order'] = str(e)

    except IntegrityError as e:
        db.session.rollback()
        if 'statuses.name' in str(e):
            errors['name'] = f'Status de Produção {status.name} já existe'
        if 'statuses.order' in str(e):
            errors['order'] = f'Ordem ({status.order}) já existe'

    finally:
        if errors['name'] is not None or errors['order'] is not None:
            return jsonify(errors), 400
        return jsonify(status.to_dict()), 201


@bp.route('status/<status_id>', methods=['GET'])
def get_status_by_id(status_id):
    status = Status.query.filter_by(id=status_id).first()
    if status is None:
        return jsonify('Status de Produção não encontrado'), 404
    return jsonify(status.to_dict()), 200


@bp.route('status/<status_id>', methods=['PATCH', 'PUT'])
def update_status(status_id):
    data = request.get_json()
    if data is None:
        return jsonify('Dados vazios'), 400

    status = Status.query.filter_by(id=status_id).first()
    if status is None:
        return jsonify('Status de Produção não encontrado'), 404

    errors = {'name': None, 'order': None}
    try:
        name = data.get('name', None)
        if name is not None and status.name != name:
            status.name = name

        order = data.get('order', None)
        if order is not None and status.order != order:
            status.order = order

        db.session.commit()

    except ValueError as e:
        db.session.rollback()
        err = str(e).lower()
        if 'status' in err:
            errors['name'] = str(e)
        if 'order' in err:
            errors['order'] = str(e)

    except IntegrityError as e:
        db.session.rollback()
        if 'statuses.name' in str(e):
            errors['name'] = f'Status de Produção {data.get("name")} já existe'
        if 'statuses.order' in str(e):
            errors['order'] = f'Ordem ({data.get("order")}) já existe'

    finally:
        if errors['name'] is not None or errors['order'] is not None:
            return jsonify(errors), 400
        return jsonify(status.to_dict()), 200


@bp.route('status/<status_id>', methods=['DELETE'])
def delete_status(status_id):
    status = Status.query.filter_by(id=status_id).first()
    if status is None:
        return jsonify('Status de Produção não encontrado'), 404

    db.session.delete(status)
    try:
        db.session.commit()
        return jsonify('Status de Produção apagado'), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify('Impossível apagar status usado em produção.'), 400
