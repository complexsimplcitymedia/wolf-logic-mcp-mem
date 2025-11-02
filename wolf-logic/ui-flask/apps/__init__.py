# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module

db = SQLAlchemy()
login_manager = LoginManager()

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)

def register_blueprints(app):
    try:
        # Register memories blueprint (main app)
        from apps.memories import blueprint as memories_blueprint
        from apps.memories import routes
        app.register_blueprint(memories_blueprint)
        print(f' > Registered blueprint: {memories_blueprint.name}')
    except Exception as e:
        print(f' > ERROR registering blueprint: {e}')
        raise

def create_app(config):

    # Contextual
    static_prefix = '/static'
    templates_dir = os.path.dirname(config.BASE_DIR)

    TEMPLATES_FOLDER = os.path.join(templates_dir,'templates')
    STATIC_FOLDER = os.path.join(templates_dir,'static')

    print(' > TEMPLATES_FOLDER: ' + TEMPLATES_FOLDER)
    print(' > STATIC_FOLDER:    ' + STATIC_FOLDER)

    app = Flask(__name__, static_url_path=static_prefix, template_folder=TEMPLATES_FOLDER, static_folder=STATIC_FOLDER)

    app.config.from_object(config)
    # Note: We don't need login_manager for memory management UI
    # register_extensions(app)
    register_blueprints(app)

    return app
