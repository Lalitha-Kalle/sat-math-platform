import os

from flask import Flask

from routes.api import api_bp
from routes.auth import auth_bp
from routes.pages import pages_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
