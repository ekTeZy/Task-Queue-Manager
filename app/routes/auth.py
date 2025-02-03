from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    url_for,
    request,
    jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    jwt_required,
    get_jwt,
    get_jwt_identity
)
from app import jwt
from app.models import User, db, Project
from app.utils import user_data_validation

auth_bp = Blueprint("auth", __name__)

blacklist = set()

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

@auth_bp.app_context_processor
def inject_user():
    """
    Добавляет текущего аутентифицированного пользователя в контекст шаблона.
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity() 
        if user_id:
            user = User.query.get(user_id)
            return {"user": user}
    except Exception:
        pass  

    return {"user": None}

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    """
    Проверяет, находится ли токен в черном списке.

    Args:
        jwt_header (dict): Заголовок JWT.
        jwt_payload (dict): Полезная нагрузка JWT.

    Returns:
        bool: True, если токен в черном списке, иначе False.
    """
    jti = jwt_payload['jti']
    return jti in blacklist

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Регистрация нового пользователя.

    Возвращает:
    - При успешной регистрации перенаправляет на страницу входа.
    - При ошибке возвращает на страницу регистрации с сообщением об ошибке.
    """
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if User.query.filter_by(email=email).first():
            flash("This email is already registered. Please try logging in.", "warning")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("This username is already taken. Please try logging in.", "warning")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "warning")
            return redirect(url_for("auth.register"))

        try:
            user_data_validation(username=username, password=password)

            user = User(
                username=username,
                email=email,
                password=password
            )

            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            flash(f"Validation error: {e}", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Вход пользователя в систему.

    Возвращает:
    - При успешном входе перенаправляет на главную страницу.
    - При ошибке возвращает на страницу входа с сообщением об ошибке.
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        try:
            user = User.check_auth(email=email, password=password)
            print(f"email {user.email}")
            if user:
                access_token, refresh_token = user.get_token(access_expired_time=1, refresh_expired_time=7)

                # print(f"access token is: {access_token}")
                # print(f"refresh token is: {refresh_token}")

                response = redirect(url_for("dashboard_presets.dashboard_step_1"))

                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                
                return response

        except Exception as e:
            flash(str(e), "danger")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html")

@auth_bp.route("/logout", methods=["GET", "POST"])
@jwt_required()
def logout():
    """
    Выход пользователя из системы.

    - Удаляет JWT токены из cookies.
    - Добавляет текущий токен в черный список.
    - Перенаправляет на страницу входа.
    """
    response = redirect(url_for("auth.login"))

    try:
        verify_jwt_in_request(optional=True)
        jti = get_jwt()["jti"]
        blacklist.add(jti)
    except Exception:
        pass 

    response.set_cookie("access_token_cookie", "", expires=0, httponly=True, samesite="Lax")
    response.set_cookie("refresh_token_cookie", "", expires=0, httponly=True, samesite="Lax")

    return response


@auth_bp.route("/profile", methods=["GET", "POST"])
@jwt_required()
def profile():
    user = User.query.get(int(get_jwt_identity()))

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    user_projects = []

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if username and username != user.username:
            if User.query.filter_by(username=username).first():
                flash(f"Username '{username}' is already taken.", "danger")
            else:
                try:
                    user_data_validation(username=username)
                    user.username = username
                    flash("Username updated successfully.", "success")
                except Exception as e:
                    flash(f"Validation error: {e}", "danger")

        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                flash(f"Email '{email}' is already taken.", "danger")
            else:
                user.email = email
                flash("Email updated successfully.", "success")

        if current_password and new_password and confirm_password:
            if not check_password_hash(user.password, current_password):
                flash("Current password is incorrect.", "danger")
            elif new_password != confirm_password:
                flash("Passwords do not match.", "danger")
            else:
                try:
                    user_data_validation(password=new_password)
                    user.password = generate_password_hash(new_password)
                    flash("Password updated successfully.", "success")

                    db.session.commit()
                    return redirect(url_for("auth.profile"))

                except Exception as e:
                    flash(str(e), "danger")
                    db.session.rollback()
                    return redirect(url_for("auth.profile"))

        db.session.commit()

        try:
            user_projects = [
                {"id": project.id, "name": project.name, "created_at": project.created_at.strftime("%Y-%m-%d")}
                for project in Project.query.filter_by(user_id=user.id).all()
            ]
        except Exception as e:
            flash(f"Error fetching projects: {str(e)}", "danger")

    return render_template("auth/profile.html", user=user, projects=user_projects)


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    """
    Обновляет access-токен с использованием refresh-токена.
    """
    user = User.query.get(get_jwt_identity()["id"])
    new_access_token, _ = user.get_token(access_expired_time=1)

    response = jsonify({"msg": "Access token refreshed"})
    set_access_cookies(response, new_access_token)
    return response, 200