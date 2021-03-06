import os
import sys
from flask import (
    Flask,
    request,
    jsonify,
    abort
)
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import (
    db_drop_and_create_all,
    setup_db,
    Drink
)
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    data = Drink.query.all()
    drinks = []

    if data:
        drinks = [drink.short() for drink in data]

    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def drink_details(payload):
    data = Drink.query.all()
    drinks = []

    if data:
        drinks = [drink.short() for drink in data]

    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def post_drinks(payload):
    body = request.get_json()
    req_title = body.get('title')
    req_recipe = body.get('recipe')

    try:
        if isinstance(req_recipe, dict):
            req_recipe = [req_recipe]

        drink = Drink(
            title=req_title,
            recipe=json.dumps(req_recipe)
        )
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": drink.long()
        })
    except BaseException:
        print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def modify_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(
            Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        body = request.get_json()
        req_title = body.get('title')

        drink.title = req_title
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except BaseException:
        print(sys.exc_info())
        abort(422)


'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(
            Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        })
    except BaseException:
        abort(422)

# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


'''
@ error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
