from functools import wraps
from flask import Blueprint, session, redirect, url_for, flash, abort
from controllers.report_controller import map_view, submit_report, report_detail

report_bp = Blueprint("report", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        if session.get("user_role") != "user":
            abort(403, description="Only citizen accounts can submit reports. Admins manage reports from the dashboard.")
        return f(*args, **kwargs)
    return decorated


report_bp.add_url_rule("/map",                    "map_view", map_view,                       methods=["GET"])
report_bp.add_url_rule("/report/submit",          "submit",   user_required(submit_report),   methods=["POST"])
report_bp.add_url_rule("/report/<int:report_id>", "detail",   report_detail,                  methods=["GET"])