from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, SubmitField, validators


class AddTerminalForm(FlaskForm):
    terminal_id = StringField(
        _l("Terminal Id"),
        [validators.InputRequired(), validators.Length(min=12, max=36)],
        render_kw={"placeholder": "uuid or uuid tail"},
    )
    recaptcha = RecaptchaField()
    submit_button = SubmitField(_l("Add new terminal"))


class AddRouteForm(FlaskForm):
    src_terminal_id = StringField(
        _l("From source Terminal Id"),
        [validators.InputRequired(), validators.Length(min=12, max=36)],
        render_kw={"placeholder": "uuid or uuid tail"},
    )
    dst_terminal_id = StringField(
        _l("To destination Terminal Id"),
        [validators.InputRequired(), validators.Length(min=12, max=36)],
        render_kw={"placeholder": "uuid or uuid tail"},
    )
    recaptcha = RecaptchaField()
    submit_button = SubmitField(_l("Add route"))
