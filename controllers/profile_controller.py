import os, uuid, requests as http_requests
from flask import render_template, redirect, url_for, session, request, flash, current_app
from werkzeug.utils import secure_filename
from models.user import User
from models.report import Report
from config import Config

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(f):
    return "." in f and f.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _upload_to_firebase(file, folder="pfp"):
    """Upload a file object to Firebase Storage, return public download URL."""
    ext      = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    filename = f"{folder}/{uuid.uuid4().hex}.{ext}"
    bucket   = Config.FIREBASE_STORAGE_BUCKET
    api_key  = Config.FIREBASE_API_KEY

    # Read file bytes
    file_bytes = file.read()
    mime = {
        "png": "image/png", "gif": "image/gif",
        "webp": "image/webp", "jpg": "image/jpeg", "jpeg": "image/jpeg"
    }.get(ext, "image/jpeg")

    # Upload via Firebase Storage REST API
    upload_url = (
        f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o"
        f"?name={requests_quote(filename)}&key={api_key}"
    )
    resp = http_requests.post(
        upload_url,
        data=file_bytes,
        headers={"Content-Type": mime},
        timeout=30
    )
    resp.raise_for_status()
    data = resp.json()

    # Build public download URL
    encoded_name = requests_quote(filename, safe="")
    download_url = (
        f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o/"
        f"{encoded_name}?alt=media&token={data.get('downloadTokens','')}"
    )
    return download_url


def requests_quote(s, safe=""):
    from urllib.parse import quote
    return quote(s, safe=safe)


def view_profile():
    user_id = session.get("user_id")
    user    = User.find_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))
    reports = Report.find_by_user(user_id)
    return render_template("profile/index.html", user=user, reports=reports)


def edit_profile():
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
            flash("Invalid date of birth format.", "error")
            return redirect(url_for("profile.view"))
    try:
        User.update_profile(user_id, bio=bio, dob=dob)
        flash("Profile updated successfully.", "success")
    except Exception as e:
        flash(f"Update failed: {str(e)}", "error")
    return redirect(url_for("profile.view"))


def upload_pfp():
    user_id = session.get("user_id")
    file    = request.files.get("pfp")
    if not file or file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("profile.view"))
    if not allowed_file(file.filename):
        flash("Invalid file type. Use PNG, JPG, or WEBP.", "error")
        return redirect(url_for("profile.view"))
    try:
        pfp_url = _upload_to_firebase(file, folder="pfp")
        User.update_pfp(user_id, pfp_url)
        session["user_pfp"] = pfp_url
        flash("Profile picture updated.", "success")
    except Exception as e:
        flash(f"Upload failed: {str(e)}", "error")
    return redirect(url_for("profile.view"))


def remove_pfp():
    user_id = session.get("user_id")
    try:
        User.update_pfp(user_id, None)
        session["user_pfp"] = None
        flash("Profile picture removed.", "info")
    except Exception as e:
        flash(f"Failed to remove picture: {str(e)}", "error")
    return redirect(url_for("profile.view"))


def change_password():
    user_id           = session.get("user_id")
    current_password  = request.form.get("current_password", "")
    new_password       = request.form.get("new_password", "")
    confirm_password   = request.form.get("confirm_password", "")

    user    = User.find_by_id(user_id)
    reports = Report.find_by_user(user_id)

    def render_with_error(error_msg):
        return render_template("profile/index.html", user=user, reports=reports,
                               pw_error=error_msg, pw_open=True)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("profile.view"))

    if not user.verify_password(current_password):
        return render_with_error("Current password is incorrect.")

    if len(new_password) < 8:
        return render_with_error("New password must be at least 8 characters.")

    if new_password != confirm_password:
        return render_with_error("New passwords do not match.")

    if user.verify_password(new_password):
        return render_with_error("New password must be different from your current password.")

    user.set_password(new_password)
    from database import db
    db.session.commit()

    flash("Password updated successfully.", "success")
    return redirect(url_for("profile.view"))