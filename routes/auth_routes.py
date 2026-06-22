from flask import Blueprint
from controllers.auth_controller import (
    home, show_login, handle_login,
    show_signup, handle_signup, logout,
    show_forgot_password, handle_forgot_password,
    show_reset_password, handle_reset_password,
)

auth_bp = Blueprint("auth", __name__)

auth_bp.add_url_rule("/",                       "home",            home,                   methods=["GET"])
auth_bp.add_url_rule("/login",                  "login",           show_login,             methods=["GET"])
auth_bp.add_url_rule("/login",                  "login_post",      handle_login,           methods=["POST"])
auth_bp.add_url_rule("/signup",                 "signup",          show_signup,            methods=["GET"])
auth_bp.add_url_rule("/signup",                 "signup_post",     handle_signup,          methods=["POST"])
auth_bp.add_url_rule("/logout",                 "logout",          logout,                  methods=["GET"])
auth_bp.add_url_rule("/forgot-password",        "forgot_password", show_forgot_password,   methods=["GET"])
auth_bp.add_url_rule("/forgot-password",        "forgot_password_post", handle_forgot_password, methods=["POST"])
auth_bp.add_url_rule("/reset-password/<token>", "reset_password",  show_reset_password,    methods=["GET"])
auth_bp.add_url_rule("/reset-password/<token>", "reset_password_post", handle_reset_password, methods=["POST"])