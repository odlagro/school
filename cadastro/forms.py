from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp, NumberRange

ROLE_CHOICES = [
    ("Diretoria", "Diretoria"),
    ("Comum", "Comum"),
]


class UsuarioForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Senha (preencher para definir/alterar)", validators=[Optional(), Length(min=6, max=128)])
    role = SelectField("Perfil", choices=ROLE_CHOICES, validators=[DataRequired()])
    active = BooleanField("Ativo")
    submit = SubmitField("Salvar")


class HorarioForm(FlaskForm):
    # Usamos HH:MM com Regexp para evitar incompatibilidades de TimeField em WTForms
    hora_inicio = StringField(
        "Hora início",
        validators=[DataRequired(), Regexp(r"^\d{2}:\d{2}$", message="Use o formato HH:MM")]
    )
    hora_fim = StringField(
        "Hora fim",
        validators=[DataRequired(), Regexp(r"^\d{2}:\d{2}$", message="Use o formato HH:MM")]
    )
    submit = SubmitField("Salvar")


class MensalidadeForm(FlaskForm):
    serie = StringField("Série", validators=[DataRequired(), Length(max=120)])
    valor = DecimalField("Valor", places=2, rounding=None, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Salvar")
