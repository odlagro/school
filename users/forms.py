# users/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, ValidationError
from models import User
from extensions import db

ROLE_CHOICES = [
    ("Diretoria", "Diretoria"),
    ("Professor", "Professor"),
    ("Aluno", "Aluno"),
    ("Pai", "Pai"),
]

PASSWORD_6_DIGITS = Regexp(r"^\d{6}$", message="A senha deve ter exatamente 6 dígitos numéricos.")

class UserCreateForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = SelectField("Perfil", choices=ROLE_CHOICES, validators=[DataRequired()])
    password = PasswordField("Senha (6 dígitos)", validators=[DataRequired(), PASSWORD_6_DIGITS])
    confirm = PasswordField("Confirmar Senha", validators=[DataRequired(), EqualTo("password", message="Senhas não conferem.")])
    submit = SubmitField("Salvar")

    def validate_email(self, field):
        if db.session.scalar(db.select(User).filter_by(email=field.data.lower())):
            raise ValidationError("Este e-mail já está cadastrado.")

class UserEditForm(FlaskForm):
    # email ficará somente leitura no template; ainda validamos caso venha alterado
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = SelectField("Perfil", choices=ROLE_CHOICES, validators=[DataRequired()])
    is_active = BooleanField("Ativo")
    submit = SubmitField("Salvar")

    def __init__(self, original_email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = (original_email or "").lower()

    def validate_email(self, field):
        new_email = field.data.lower()
        if new_email != self.original_email:
            if db.session.scalar(db.select(User).filter_by(email=new_email)):
                raise ValidationError("Este e-mail já está cadastrado em outra conta.")

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField("Senha atual", validators=[DataRequired()])
    new_password = PasswordField("Nova senha (6 dígitos)", validators=[DataRequired(), PASSWORD_6_DIGITS])
    confirm_new_password = PasswordField("Confirmar nova senha", validators=[DataRequired(), EqualTo("new_password", message="Senhas não conferem.")])
    submit = SubmitField("Atualizar senha")

class DeleteForm(FlaskForm):
    # usado só para CSRF/submit em exclusão
    submit = SubmitField("Excluir")
