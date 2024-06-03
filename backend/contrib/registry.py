import os.path
import logging
import traceback
from flask import Flask, jsonify, Response

import flask_jwt_extended as flask_jwt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity

from .auth_guard.api import ag_blueprint
from .auth_guard import config as settings
from .auth_guard.utils import get_user
from .utils.module_loading import import_string

__all__ = ["RegistryApps"]
logger = logging.getLogger("vector-vein")


class CallableError(Exception):
	pass


class RegistryApps:
	def __init__(self, app: Flask):
		self.app = app

	def user_lookup_callback(self, jwt_header, jwt_data):
		identity = jwt_data[self.app.config["JWT_IDENTITY_CLAIM"]]
		return get_user(userid=identity["user_id"])

	def error_handler(self, e: BaseException) -> Response:
		logger.error("In error_handler >>>>>>>>>>>>>>>>>>")
		logger.error(traceback.format_exc())
		logger.error("In error_handler <<<<<<<<<<<<<<<<<<")

		return jsonify(dict(code=500, status="error", msg=str(e), data=None))

	def register_extensions(self):
		# jwt
		for jwt_key, jwt_value in settings.JWT.items():
			self.app.config[jwt_key] = jwt_value

		jwt = JWTManager(self.app)
		jwt.user_lookup_loader(self.user_lookup_callback)  # Automatic user loading

	def register_blueprints(self):
		self.app.register_blueprint(ag_blueprint)

	def register_middlewares(self):
		for middleware_path in reversed(settings.MIDDLEWARES):
			try:
				middleware = import_string(middleware_path)
				mw_instance = middleware(app=self.app)

				if not callable(mw_instance):
					raise CallableError("middleware: %s must callable.")

				mw_instance.logger = logger
			except (ImportError, CallableError) as e:
				logger.error(traceback.format_exc())
				raise e
			else:
				self.app.before_request(mw_instance.__call__)

	def ready(self):
		self.register_extensions()

		# Default on middlewares
		middleware_active = os.environ.get("MIDDLEWARE_ACTIVE", "off")  # ["on", "off"]
		logger.info("`MIDDLEWARE_ACTIVE` is [%s] in RegistryApps", middleware_active)

		# >>>>> 等待后续处理（jwt token） <<<<<
		# if middleware_active == "on":
		# 	self.register_middlewares()

		self.register_blueprints()
		# self.app.register_error_handler(Exception, self.error_handler)



