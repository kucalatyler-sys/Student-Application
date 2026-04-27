import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail

from .modles import User, db

mail = Mail()


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def ensure_sqlite_schema(database_path):
    connection = sqlite3.connect(database_path)
    try:
        existing_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(applications)").fetchall()
        }
        if 'UserID' not in existing_columns:
            connection.execute('ALTER TABLE applications ADD COLUMN UserID INTEGER')
            connection.commit()
    finally:
        connection.close()

def create_app():
    # Load .env from the project root (one level above this package)
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'it-is-a-secret'
    database_path = Path(__file__).resolve().parent / 'students.db'
    schema_path = Path(__file__).resolve().parent / 'students.sql'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{database_path.as_posix()}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Email / Flask-Mail ────────────────────────────────────────────────────
    app.config['MAIL_SERVER']   = os.getenv('MAIL_SERVER',   'smtp.gmail.com')
    app.config['MAIL_PORT']     = int(os.getenv('MAIL_PORT', '587'))
    app.config['MAIL_USE_TLS']  = os.getenv('MAIL_USE_TLS',  'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME', 'no-reply@scsu.edu'))
    app.config['APP_BASE_URL']  = os.getenv('APP_BASE_URL',  'http://localhost:5000')

    if not app.config['MAIL_USERNAME']:
        import warnings
        warnings.warn(
            "MAIL_USERNAME is not set — email notifications will not be sent. "
            "Copy .env.example to .env and fill in your credentials.",
            RuntimeWarning,
            stacklevel=2,
        )

    if (
        app.config['SQLALCHEMY_DATABASE_URI'] == f"sqlite:///{database_path.as_posix()}"
        and not database_path.exists()
        and schema_path.exists()
    ):
        connection = sqlite3.connect(database_path)
        try:
            connection.executescript(schema_path.read_text(encoding='utf-8'))
            connection.commit()
        finally:
            connection.close()

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'error'
    login_manager.login_message = 'Please log in to continue.'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()
        if app.config['SQLALCHEMY_DATABASE_URI'] == f"sqlite:///{database_path.as_posix()}":
            ensure_sqlite_schema(database_path)

    return app
