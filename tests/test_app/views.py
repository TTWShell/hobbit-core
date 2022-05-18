from flask import Blueprint, jsonify
from marshmallow import fields
from marshmallow.utils import missing
from webargs.flaskparser import use_kwargs as base_use_kwargs

from hobbit_core.utils import use_kwargs
from hobbit_core.db import transaction

from .schemas import UserSchema
from .exts import db
from .models import User

bp = Blueprint('test', __name__)


def wrapper_kwargs(kwargs):
    res = {}
    for k, v in kwargs.items():
        if v is missing:
            res[k] = 'missing'
            continue
        res[k] = v
    return res


@bp.route('/use_kwargs_with_partial/', methods=['POST'])
@use_kwargs(UserSchema(partial=True, exclude=['role']))
def use_kwargs_with_partial(**kwargs):
    return jsonify(wrapper_kwargs(kwargs))


@bp.route('/use_kwargs_without_partial/', methods=['POST'])
@use_kwargs(UserSchema(exclude=['role']))
def use_kwargs_without_partial(**kwargs):
    return jsonify(wrapper_kwargs(kwargs))


@bp.route('/use_kwargs_dictargmap_partial/', methods=['POST'])
@use_kwargs({
    'username': fields.Str(missing=None),
    'password': fields.Str(allow_none=True),
}, schema_kwargs={'partial': True})
def use_kwargs_dictargmap_partial(**kwargs):
    return jsonify(wrapper_kwargs(kwargs))


@bp.route('/base_use_kwargs_dictargmap_partial/', methods=['POST'])
@base_use_kwargs({
    'username': fields.Str(missing=None),
    'password': fields.Str(allow_none=True),
})
def base_use_kwargs_dictargmap_partial(**kwargs):
    return jsonify(wrapper_kwargs(kwargs))


@bp.route('/create_user/success/', methods=['POST'])
@base_use_kwargs({'email': fields.Str()})
def create_user_success(email):
    @transaction(db.session, nested=None)
    def create_user():
        user1 = User(username='signalling_test', email=email, password='1')
        db.session.add(user1)

    create_user()
    return jsonify({})


@bp.route('/create_user/failed/', methods=['POST'])
@base_use_kwargs({'email': fields.Str()})
def create_user_failed(email):
    @transaction(db.session)
    def create_user():
        user1 = User(username='signalling_test', email=email, password='1')
        db.session.add(user1)

    create_user()
    return jsonify({})
