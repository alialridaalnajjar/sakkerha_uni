from datetime import timedelta, date, datetime
from flask import render_template, redirect, url_for, session, request, flash, current_app
from models.user import User
from models.builders.user_builder import UserBuilder
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


# ── Session helper ────────────────────────────────────────
def _login_user(user, remember=False):
    session.clear()
    session.permanent = True
    from flask import current_app
    current_app.permanent_session_lifetime = (
        timedelta(days=30) if remember else timedelta(days=7)
    )
    session["user_id"]       = user.id
    session["user_role"]     = user.role
    session["user_name"]     = user.full_name
    session["user_username"] = user.username or user.first_name
    session["initials"]      = user.initials
    session["user_pfp"]      = user.image_pfp


# ── Home ──────────────────────────────────────────────────
def home():
    return render_template("home/index.html")


# ── Login ─────────────────────────────────────────────────
def show_login():
    if "user_id" in session:
        return _redirect_by_role()
    return render_template("auth/login.html")


def handle_login():
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    remember = request.form.get("remember") == "on"

    user = User.find_by_email(email)
    if not user or not user.verify_password(password):
        return render_template("auth/login.html",
                               login_error="Invalid email or password.",
                               prefill_email=email)

    _login_user(user, remember=remember)
    return _redirect_by_role()


# ── Signup ────────────────────────────────────────────────
def show_signup():
    if "user_id" in session:
        return _redirect_by_role()
    return render_template("auth/signup.html")


def handle_signup():
    first_name = request.form.get("first_name", "").strip()
    last_name  = request.form.get("last_name",  "").strip()
    username   = request.form.get("username",   "").strip()
    dob_str    = request.form.get("dob",        "").strip()
    email      = request.form.get("email",      "").strip().lower()
    password   = request.form.get("password",   "")
    confirm    = request.form.get("confirm",    "")

    prefill = {
        "first_name": first_name, "last_name": last_name,
        "username": username, "dob": dob_str, "email": email,
    }

    # ── Validation ────────────────────────────────────────
    if not all([first_name, last_name, username, email, password, confirm]):
        return render_template("auth/signup.html", signup_error="All fields are required.", prefill=prefill)

    if password != confirm:
        return render_template("auth/signup.html", signup_error="Passwords do not match.", prefill=prefill)

    if len(password) < 8:
        return render_template("auth/signup.html", signup_error="Password must be at least 8 characters.", prefill=prefill)

    if User.find_by_email(email):
        return render_template("auth/signup.html", signup_error="An account with that email already exists.", prefill=prefill)

    if User.find_by_username(username):
        return render_template("auth/signup.html", signup_error="That username is already taken.", prefill=prefill)

    # Parse DOB
    dob = None
    if dob_str:
        try:
            parts = dob_str.split("-")
            dob = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except Exception:
            return render_template("auth/signup.html", signup_error="Invalid date of birth.", prefill=prefill)

    # ── Build & save ──────────────────────────────────────
    try:
        user = (UserBuilder()
                .set_name(first_name, last_name)
                .set_username(username)
                .set_email(email)
                .set_password(password)
                .set_dob(dob)
                .set_role("user")
                .build()
                .save())
        _login_user(user, remember=False)
        flash(f"Welcome to Sakkerha, @{username}!", "success")
        return redirect(url_for("report.map_view"))
    except Exception as e:
        return render_template("auth/signup.html", signup_error=f"Registration failed: {str(e)}", prefill=prefill)


# ── Logout ────────────────────────────────────────────────
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.home"))


# ── Forgot password ───────────────────────────────────────
def _get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def show_forgot_password():
    return render_template("auth/forgot_password.html")


def handle_forgot_password():
    email = request.form.get("email", "").strip().lower()
    user  = User.find_by_email(email)

    # Rate limit: max 1 reset email per 5 minutes per address, tracked in session
    cooldown_key = f"reset_cooldown_{email}"
    last_sent    = session.get(cooldown_key)
    if last_sent:
        elapsed = (datetime.utcnow() - datetime.fromisoformat(last_sent)).total_seconds()
        if elapsed < 300:
            wait = int(300 - elapsed)
            return render_template("auth/forgot_password.html",
                                   forgot_error=f"Please wait {wait}s before requesting another reset email.")

    # Always show the same success message whether or not the email exists —
    # this prevents leaking which emails are registered (basic security practice)
    if user:
        from flask_mail import Message
        from app import mail

        serializer = _get_serializer()
        token      = serializer.dumps(email, salt="password-reset")
        reset_url  = url_for("auth.reset_password", token=token, _external=True)

        try:
            msg = Message(
                subject="Reset your Sakkerha password",
                recipients=[email],
                body=(
                    f"Hi {user.first_name},\n\n"
                    f"We received a request to reset your Sakkerha password.\n"
                    f"Click the link below to set a new password. This link expires in 30 minutes:\n\n"
                    f"{reset_url}\n\n"
                    f"If you didn't request this, you can safely ignore this email.\n\n"
                    f"— Sakkerha"
                ),
            )
            mail.send(msg)
        except Exception as e:
            print(f"[Mail Error] {e}")

        session[cooldown_key] = datetime.utcnow().isoformat()

    flash("If an account exists with that email, a reset link has been sent.", "info")
    return redirect(url_for("auth.login"))


def show_reset_password(token):
    serializer = _get_serializer()
    try:
        email = serializer.loads(token, salt="password-reset", max_age=1800)  # 30 min
    except SignatureExpired:
        flash("This reset link has expired. Please request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("This reset link is invalid.", "error")
        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/reset_password.html", token=token)


def handle_reset_password(token):
    serializer = _get_serializer()
    try:
        email = serializer.loads(token, salt="password-reset", max_age=1800)
    except SignatureExpired:
        flash("This reset link has expired. Please request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("This reset link is invalid.", "error")
        return redirect(url_for("auth.forgot_password"))

    new_password     = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if len(new_password) < 8:
        return render_template("auth/reset_password.html", token=token,
                               reset_error="Password must be at least 8 characters.")
    if new_password != confirm_password:
        return render_template("auth/reset_password.html", token=token,
                               reset_error="Passwords do not match.")

    user = User.find_by_email(email)
    if not user:
        flash("Account not found.", "error")
        return redirect(url_for("auth.login"))

    user.set_password(new_password)
    from database import db
    db.session.commit()

    flash("Password reset successfully. You can now log in.", "success")
    return redirect(url_for("auth.login"))


# ── Internal ──────────────────────────────────────────────
def _redirect_by_role():
    if session.get("user_role") == "admin":
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("report.map_view"))