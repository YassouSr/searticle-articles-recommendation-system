from wtforms import (
    Form,
    StringField,
    validators,
    PasswordField,
    ValidationError,
    SearchField,
)
from app.models import Profile


# Global variables
first_name_field = StringField(
    "prénom",
    [
        validators.length(
            min=2,
            max=10,
            message="First name must be at least 2 characters and maximum 10 characters.",
        ),
        validators.DataRequired(message="Please enter your first name."),
    ],
)

last_name_field = StringField(
    "nom",
    [
        validators.length(
            min=2,
            max=10,
            message="First name must be at least 2 characters and maximum 10 characters.",
        ),
        validators.DataRequired(message="Please enter your first name."),
    ],
)

email_field = StringField(
    "email",
    [
        validators.Email(message="That's not a valid email address."),
        validators.DataRequired(message="Please enter your email address."),
    ],
)

password_field = PasswordField(
    "mot de passe",
    [
        validators.length(min=5, message="Password must be at least 5 characters."),
        validators.DataRequired(message="Please enter your password."),
    ],
)


class RegistrationForm(Form):
    first_name = first_name_field
    last_name = last_name_field
    email = email_field
    password = password_field

    def validate_email(self, email):
        user = Profile.query.filter_by(
            email=email.data
        ).first()  # Check if the email already exists
        if user:
            raise ValidationError(
                "L'e-mail donné est pris. veuillez choisir une autre adresse e-mail."
            )


class LoginForm(Form):
    email = email_field
    password = password_field


class ResetPasswordForm(Form):
    email = email_field


class ResetPasswordConfirmForm(Form):
    password = password_field


class ProfileForm(Form):
    first_name = first_name_field
    last_name = last_name_field
    email = email_field


class SearchForm(Form):
    q = SearchField("rechercher")
