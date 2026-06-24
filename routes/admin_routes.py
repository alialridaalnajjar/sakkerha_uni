from functools import wraps
from flask import Blueprint, session, redirect, url_for, flash, abort
from controllers.admin_controller import (
    map_view, dashboard, report_detail, update_status, update_status_form,
    delete_report_form,
    admin_profile, admin_edit_profile, admin_upload_pfp, admin_remove_pfp
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        if session.get("user_role") != "admin":
            abort(403, description="This area is restricted to administrators only.")
        return f(*args, **kwargs)
    return decorated


admin_bp.add_url_rule("/",                              "dashboard",    admin_required(dashboard),          methods=["GET"])
admin_bp.add_url_rule("/map",                           "map_view",     admin_required(map_view),           methods=["GET"])
admin_bp.add_url_rule("/profile",                       "profile",      admin_required(admin_profile),      methods=["GET"])
admin_bp.add_url_rule("/profile/edit",                  "edit_profile", admin_required(admin_edit_profile), methods=["POST"])
admin_bp.add_url_rule("/profile/pfp/upload",            "upload_pfp",   admin_required(admin_upload_pfp),   methods=["POST"])
admin_bp.add_url_rule("/profile/pfp/remove",            "remove_pfp",   admin_required(admin_remove_pfp),   methods=["POST"])
admin_bp.add_url_rule("/report/<int:report_id>",             "report_detail",      admin_required(report_detail),      methods=["GET"])
admin_bp.add_url_rule("/report/<int:report_id>/status",      "update_status",      admin_required(update_status),      methods=["POST"])
admin_bp.add_url_rule("/report/<int:report_id>/status-form", "update_status_form", admin_required(update_status_form), methods=["POST"])
admin_bp.add_url_rule("/report/<int:report_id>/delete-form", "delete_report_form", admin_required(delete_report_form), methods=["POST"])