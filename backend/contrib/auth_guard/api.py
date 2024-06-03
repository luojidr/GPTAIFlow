from flask import Blueprint
from flask import jsonify, request
from werkzeug import exceptions

from flask_jwt_extended import create_access_token, current_user

from .utils import get_user

ag_blueprint = Blueprint("auth_guard", __name__, url_prefix="/auth")


@ag_blueprint.route("/token/get", methods=["POST", "GET"])
def get_jwt_token():
	""" Obtain jwt token from web log page, token payload eg:
	Returns jsonify
	"""
	# AI机器人不会走这个接口
	# 前端设置header -> Authorization
	if request.method != "POST":
		raise exceptions.MethodNotAllowed(f"the request method({request.method}) is not allowed!")

	payload = request.json
	user_obj = get_user(username=payload.get("user_name"))

	if not user_obj.check_password(password=payload.get("password")):
		return jsonify(msg='用户名/密码校验失败', status=200)

	access_token = create_access_token(
		identity=dict(
			username=user_obj.user_name,
			user_id=user_obj.user_id,
		)
	)
	return jsonify(msg='ok', status=200, data=dict(access_token=access_token))


@ag_blueprint.route('/userinfo/get', methods=["POST"])
def get_userinfo():
	""" use jwt token to get userinfo """
	return jsonify(msk="ok", status=200, data=dict(user_id=str(current_user.user_id), role=current_user.role))


@ag_blueprint.route("/token/check", methods=["GET"])
def check_jwt_token():
	""" use middleware to authenticate token """
	return jsonify(msg='check jwt token is successful', status=200)
