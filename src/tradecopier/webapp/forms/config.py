from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators


class AddTerminalForm(FlaskForm):
    terminal_id = StringField(
        "Terminal Id",
        [validators.InputRequired(), validators.UUID()],
        render_kw={"placeholder": "123e4567-e89b-12d3-a456-426614174000"},
    )
    submit_button = SubmitField(_l("Add new terminal"))
