from app.config import DevConfig, ProdConfig
from flask import Flask, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()
migrate = Migrate()


def create_app(*args, **kwargs):
    app = Flask(__name__)

    # init config
    app.config.from_object(DevConfig())
    if os.environ.get('FLASK_ENV', 'production') == 'production':
        app.config.from_object(ProdConfig())

    # init extensions
    Bcrypt(app)
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # init blueprints
    from app.blueprints import batches, materials, products, suppliers, units
    app.register_blueprint(batches.bp)
    app.register_blueprint(materials.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(suppliers.bp)
    app.register_blueprint(units.bp)

    @app.shell_context_processor
    def ctx():
        return {
            'app': app,
            'db': db,
        }

    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return jsonify('<strong>O recurso solicitado não foi encontrado.</strong><hr/>Verifique o endereço ou contate seu administrador de sistemas.'), 404

    @app.route('/')
    def index():
        return 'ERP FREE'

    return app
