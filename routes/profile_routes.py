from functools import wraps
from flask import Blueprint, session, redirect, url_for, flash, abort
from controllers.profile_controller import view_profile, edit_profile, upload_pfp, remove_pfp, change_password

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        if session.get("user_role") == "admin":
            abort(403, description="Admins have a separate profile page at /admin/profile.")
        return f(*args, **kwargs)
    return decorated


profile_bp.add_url_rule("/",                "view",            login_required(view_profile),     methods=["GET"])
profile_bp.add_url_rule("/edit",            "edit",            login_required(edit_profile),     methods=["POST"])
profile_bp.add_url_rule("/pfp/upload",      "upload_pfp",      login_required(upload_pfp),       methods=["POST"])
profile_bp.add_url_rule("/pfp/remove",      "remove_pfp",      login_required(remove_pfp),       methods=["POST"])
profile_bp.add_url_rule("/change-password", "change_password", login_required(change_password),  methods=["POST"])