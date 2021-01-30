from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, SubmitField, validators


class LoginForm(FlaskForm):
    terminal_id = StringField(
        _l("Your Terminal Id"),
        [validators.InputRequired(), validators.UUID()],
        render_kw={"placeholder": "123e4567-e89b-12d3-a456-426614174000"},
    )
    recaptcha = RecaptchaField()
    submit_button = SubmitField(_l("Log In"))
