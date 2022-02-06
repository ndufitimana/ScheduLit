from app.api import bp 
from app.models import User
from flask import jsonify, request, url_for, abort
from app import db
from app.api.errors import bad_request
from app.api.auth import basic_auth, token_auth

@bp.route('/users/<int:id>', methods = ["GET"])
@token_auth.login_required
def get_user(id):
    """ This route returns a user given an id """
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/users/<int:id>/followers', methods = ["GET"])
def get_followers(id):
    """This route returns the followers of a given user given 
    the user id"""
    pass
@bp.route('/users', methods = ["POST"])
def create_user():
    """ This route registers a new user """
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email, and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Please user a different username')
    if User.query.filter_by(email= data['email']).first():
        return bad_request('Please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    #the following line is required for http protocol
    response.headers['Location'] = url_for('api.get_user', id = user.id) 
    return response

@bp.route('/users/<int:id>', methods = ["PUT"])
@token_auth.login_required
def update_user(id):
    """ This route updates a user given a user id """
    user = User.query.get_or_404(id)
    data = request.get_json() or {}

    if token_auth.current_user().id != id: #can only update yourself not others
        abort(403)

    if 'username' in data and data['username'] != user.username and \
        User.query.filter_by(username= data['username']).first():
        return bad_request('Please use a different username')
    if 'email' in data and data['email']!= user.email and \
        User.query.filter_by(email= data['email']).first():
        return bad_request('Please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())
@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token() #get token from User Model
    db.session.commit()
    return jsonify({'token': token})

