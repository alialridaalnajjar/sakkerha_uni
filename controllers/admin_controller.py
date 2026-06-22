import json, os, uuid
from flask import render_template, redirect, url_for, request, flash, jsonify, session, current_app
from werkzeug.utils import secure_filename
from models.report import Report
from models.user import User
from config import Config

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(f):
    return "." in f and f.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Admin map (view only) ─────────────────────────────────
def map_view():
    public_reports = Report.find_public()
    reports_json = json.dumps([{
        "id":          r.id,
        "lat":         float(r.latitude),
        "lng":         float(r.longitude),
        "description": r.description,
        "severity":    r.severity,
        "status":      r.status,
        "reporter":    r.reporter_name,
        "images":      r.images,
        "created_at":  r.created_at.strftime("%b %d, %Y") if r.created_at else "",
    } for r in public_reports])
    return render_template("admin/map.html", reports_json=reports_json)


# ── Dashboard ─────────────────────────────────────────────
def dashboard():
    status   = request.args.get("status",   "").strip() or None
    severity = request.args.get("severity", "").strip() or None
    search   = request.args.get("search",   "").strip() or None
    show_invalid = request.args.get("show_invalid") == "1"

    reports  = Report.find_all(status=status, severity=severity, search=search,
                                exclude_invalid=not show_invalid)
    invalid_count = len(Report.find_all(status="invalid"))

    return render_template(
        "admin/dashboard.html",
        reports=reports,
        filters={"status": status or "", "severity": severity or "", "search": search or ""},
        statuses=[s for s in Report.STATUSES if s != "invalid"],
        severities=[s for s in Report.SEVERITIES if s != "invalid"],
        show_invalid=show_invalid,
        invalid_count=invalid_count,
    )


# ── Report detail ─────────────────────────────────────────
def report_detail(report_id):
    report = Report.find_by_id(report_id)
    if not report:
        flash("Report not found.", "error")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/report_detail.html", report=report)


# ── Update status ─────────────────────────────────────────
def update_status(report_id):
    data       = request.get_json(silent=True) or {}
    new_status = data.get("status", "").strip()
    if new_status not in Report.STATUSES:
        return jsonify({"ok": False, "error": f"Invalid status: {new_status}"}), 400
    report = Report.find_by_id(report_id)
    if not report:
        return jsonify({"ok": False, "error": "Report not found."}), 404
    if report.status in ("completed", "rejected"):
        return jsonify({"ok": False, "error": f"Cannot change a {report.status} report."}), 400
    Report.update_status(report_id, new_status)
    return jsonify({"ok": True, "new_status": new_status})


# ── Admin profile ─────────────────────────────────────────
def admin_profile():
    user_id         = session.get("user_id")
    user            = User.find_by_id(user_id)
    ongoing_reports = Report.find_all(status="ongoing")
    all_reports     = Report.find_all()
    return render_template("admin/profile.html",
                           user=user,
                           ongoing_reports=ongoing_reports,
                           all_reports=all_reports)


def admin_edit_profile():
    user_id = session.get("user_id")
    bio     = request.form.get("bio", "").strip()
    dob_str = request.form.get("dob", "").strip() or None
    dob = None
    if dob_str:
        try:
            from datetime import date
            parts = dob_str.split("-")
            dob = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except Exception:
            flash("Invalid date of birth.", "error")
            return redirect(url_for("admin.profile"))
    User.update_profile(user_id, bio=bio, dob=dob)
    flash("Profile updated.", "success")
    return redirect(url_for("admin.profile"))


def _upload_to_firebase(file, folder="pfp"):
    """Upload file to Firebase Storage, return public download URL."""
    import requests as http_req
    from urllib.parse import quote
    ext      = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    filename = f"{folder}/{uuid.uuid4().hex}.{ext}"
    bucket   = Config.FIREBASE_STORAGE_BUCKET
    api_key  = Config.FIREBASE_API_KEY
    mime = {"png":"image/png","gif":"image/gif","webp":"image/webp"}.get(ext,"image/jpeg")
    file_bytes = file.read()
    upload_url = (
        f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o"
        f"?name={quote(filename)}&key={api_key}"
    )
    resp = http_req.post(upload_url, data=file_bytes,
                         headers={"Content-Type": mime}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    encoded = quote(filename, safe="")
    return (f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o/"
            f"{encoded}?alt=media&token={data.get('downloadTokens','')}")


def admin_upload_pfp():
    user_id = session.get("user_id")
    file    = request.files.get("pfp")
    if not file or file.filename == "" or not allowed_file(file.filename):
        flash("Invalid file.", "error")
        return redirect(url_for("admin.profile"))
    try:
        pfp_url = _upload_to_firebase(file, folder="pfp")
        User.update_pfp(user_id, pfp_url)
        session["user_pfp"] = pfp_url
        flash("Profile picture updated.", "success")
    except Exception as e:
        flash(f"Upload failed: {str(e)}", "error")
    return redirect(url_for("admin.profile"))


def admin_remove_pfp():
    User.update_pfp(session.get("user_id"), None)
    session["user_pfp"] = None
    flash("Profile picture removed.", "info")
    return redirect(url_for("admin.profile"))