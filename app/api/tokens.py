from app.api.auth import token_auth
from app.api import bp
from app import db
"""
This module will the module handling authentication for our api users
"""

def get_token():
    pass
@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204
