from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.secret_key = "trackexpenseapp"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense-tracker.db"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/", static_folder="static", template_folder = "templates")
    app.register_blueprint(auth, url_prefix="/", static_folder="static", template_folder = "templates")



    from .models import User , Budget , Expense

    @app.before_first_request
    def create_tables():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app