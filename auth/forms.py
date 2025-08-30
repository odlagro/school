# school/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length

ROLE_CHOICES = [
    ("Diretoria", "Diretoria"),
    ("Professor", "Professor"),
    ("Aluno", "Aluno"),
    ("Pai", "Pai"),
]

DIGITS_6 = Regexp(r"^\d{6}$", message="A senha deve ter exatamente 6 dígitos numéricos.")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired(), DIGITS_6])
    remember = BooleanField("Manter conectado")
    submit = SubmitField("Entrar")

class RegisterForm(FlaskForm):
    name = StringField("Nome completo")
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Senha (6 dígitos)", validators=[DataRequired(), Length(min=6, max=6), DIGITS_6]
    )
    confirm_password = PasswordField(
        "Confirmar senha",
        validators=[DataRequired(), EqualTo("password", message="Senhas não conferem")],
    )
    role = SelectField("Tipo de usuário", choices=ROLE_CHOICES, validators=[DataRequired()])
    submit = SubmitField("Criar conta")

class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Enviar link de redefinição")

class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Nova senha (6 dígitos)", validators=[DataRequired(), Length(min=6, max=6), DIGITS_6]
    )
    confirm_password = PasswordField(
        "Confirmar nova senha",
        validators=[DataRequired(), EqualTo("password", message="Senhas não conferem")],
    )
    submit = SubmitField("Redefinir senha")

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Senha atual", validators=[DataRequired(), DIGITS_6])
    new_password = PasswordField(
        "Nova senha (6 dígitos)", validators=[DataRequired(), Length(min=6, max=6), DIGITS_6]
    )
    confirm_new_password = PasswordField(
        "Confirmar nova senha",
        validators=[DataRequired(), EqualTo("new_password", message="Senhas não conferem")],
    )
    submit = SubmitField("Alterar senha")
