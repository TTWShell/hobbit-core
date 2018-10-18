from flask import Blueprint, jsonify

from hobbit_core.flask_hobbit.utils import use_kwargs

from .schemas import UserSchema

bp = Blueprint('test', __name__)


@bp.route('/use_kwargs_with_partial/', methods=['POST'])
@use_kwargs(UserSchema(partial=True))
def use_kwargs_with_partial(**kwargs):
    print(kwargs)
    return jsonify({k: v or None for k, v in kwargs.items()})


@bp.route('/use_kwargs_without_partial/', methods=['POST'])
@use_kwargs(UserSchema())
def use_kwargs_without_partial(**kwargs):
    print(kwargs)
    return jsonify({k: v or None for k, v in kwargs.items()})
