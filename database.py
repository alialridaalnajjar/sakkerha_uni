from flask_sqlalchemy import SQLAlchemy

# Single shared db instance — imported by models and app
db = SQLAlchemy()


def init_db(app):
    """Bind SQLAlchemy to the Flask app and create all tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("[DB] Tables ready (SQLAlchemy).")