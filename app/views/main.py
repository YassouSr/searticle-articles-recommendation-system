import jwt, time, os
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from app.models import Profile, db
from sqlalchemy.exc import DataError
from app.forms import (
    RegistrationForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordConfirmForm,
)
from flask_mail import Mail, Message


main = Blueprint("main", __name__)
login_manager = LoginManager()
login_manager.login_view = "main.login"
mail = Mail()


def send_token_email(user, expiration=500):
    token = jwt.encode(
        {"id": user.id, "exp": time.time() + expiration},
        key=os.environ.get("SECRET_KEY"),
    )

    msg = Message()
    msg.subject = "Réinitialiser le mot de passe pour le site Searticle"
    msg.recipients = [user.email]
    msg.sender = os.environ.get("HOST_USER")
    msg.body = f"""Pour réinitialiser votre mot de passe, visitez le lien suivant : {url_for('main.reset_password_confirm', token=token, _external=True)} 
    
    Si vous n'avez pas fait cette demande, ignorez simplement cet e-mail et aucune modification ne sera apportée.
    """
    mail.send(msg)


@login_manager.user_loader
def load_user(user_id):
    """Get authenticated user from session

    Args:
        user_id (string): stored user id in session.
    Returns:
        Profile object: user object with id = user_id
    """
    return Profile.query.get(int(user_id))


@main.route("/")
def index():
    return render_template("main/index.html")


@main.route("/register", methods=("GET", "POST"))
def register():
    form = RegistrationForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for("account.home"))

    if request.method == "POST" and form.validate():
        try:
            user = Profile(**form.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("main.login"))
        except DataError:
            flash(
                "Chaîne très longue pour l'entrée donnée, veuillez choisir une autre chaîne d'entrée.",
                "error",
            )
        except Exception as e:
            flash(str(e), "error")
    else:
        for err in form.errors.values():
            flash(err[0], "error")

    return render_template("main/register.html", form=form)


@main.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for("account.home"))

    if request.method == "POST" and form.validate():
        user = Profile.query.filter_by(email=form.email.data).first()

        if user:
            if user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for("account.home"))
            else:
                flash("Mot de passe incorrecte.", "error")
        else:
            flash(
                "Aucun utilisateur avec les informations d'identification fournies.",
                "error",
            )
    else:
        for err in form.errors.values():
            flash(err[0], "error")

    return render_template("main/login.html", form=form)


@main.route("/logout", methods=("GET", "POST"))
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@main.route("/reset-password", methods=("GET", "POST"))
def reset_password():
    form = ResetPasswordForm(request.form)

    if request.method == "POST" and form.validate():
        user = Profile.query.filter_by(email=form.email.data).first()
        if user:
            send_token_email(user)
            flash(
                "Un e-mail a été envoyé à votre adresse e-mail. Si vous n'avez pas reçu d'e-mail, veuillez fournir une adresse e-mail valide ou envoyer un autre e-mail.",
                "success",
            )
        else:
            flash(
                "Aucun utilisateur avec les informations d'identification fournies.",
                "error",
            )

    return render_template("main/reset_password.html", form=form)


@main.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password_confirm(token):
    form = ResetPasswordConfirmForm(request.form)

    try:
        user_id = jwt.decode(
            token, key=os.environ.get("SECRET_KEY"), algorithms=["HS256"]
        )["id"]
        user = Profile.query.filter_by(id=user_id).first()
    except:
        flash("Lien invalide ou expiré.", "error")
        return redirect(url_for("main.reset_password"))

    if request.method == "POST" and form.validate():  # Validation Success
        print("inside reset if")
        user.password = user.generate_hash_password(form.password.data)
        db.session.commit()
        flash(
            "Votre mot de passe a été mis à jour ! Vous pouvez maintenant vous connecter.",
            "success",
        )

        return redirect(url_for("main.login"))

    if form.errors:  # Validation Error
        for err in form.errors.values():
            flash(err[0], "error")

    return render_template("main/reset_password_confirm.html", form=form)
