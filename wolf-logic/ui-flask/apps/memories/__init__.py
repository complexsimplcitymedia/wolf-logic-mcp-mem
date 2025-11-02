# -*- encoding: utf-8 -*-
"""
Memory Management Blueprint
"""

from flask import Blueprint

blueprint = Blueprint(
    'memories_blueprint',
    __name__,
    url_prefix=''
)
