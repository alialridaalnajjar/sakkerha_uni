from flask import Flask
from flask_mail import Mail
from config import Config
from database import init_db

app = Flask(__name__)
app.config.from_object(Config)

# ── SQLAlchemy URI (Flask-SQLAlchemy uses SQLALCHEMY_DATABASE_URI) ────
app.config["SQLALCHEMY_DATABASE_URI"]    = Config.DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ── Mail ──────────────────────────────────────────────────
mail = Mail(app)

# ── Initialize ORM + create tables ───────────────────────
init_db(app)

# ── Register Blueprints ───────────────────────────────────
from routes.auth_routes    import auth_bp
from routes.report_routes  import report_bp
from routes.admin_routes   import admin_bp
from routes.profile_routes import profile_bp

app.register_blueprint(auth_bp)
app.register_blueprint(report_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profile_bp)

# ── Root redirect ─────────────────────────────────────────
from flask import redirect, url_for, render_template

@app.route("/")
def index():
    return redirect(url_for("auth.home"))


# ── Global error handlers ─────────────────────────────────
@app.errorhandler(403)
def forbidden(e):
    message = getattr(e, "description", None)
    return render_template("errors/403.html", message=message), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("errors/403.html",
                           message="The page you're looking for doesn't exist."), 404

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])