# school/cadastro/forms.py
from decimal import ROUND_HALF_UP
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields import TimeField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError


class HorarioForm(FlaskForm):
    hora_inicio = TimeField("Hora início", validators=[DataRequired(message="Informe a hora de início.")])
    hora_fim = TimeField("Hora fim", validators=[DataRequired(message="Informe a hora de término.")])
    submit = SubmitField("Salvar")

    def validate_hora_fim(self, field):
        hi = self.hora_inicio.data
        hf = field.data
        if hi and hf and hf <= hi:
            raise ValidationError("A Hora fim deve ser maior que a Hora início.")


class MensalidadeForm(FlaskForm):
    serie = StringField("Série", validators=[DataRequired(message="Informe a série."), Length(max=120)])
    valor = DecimalField(
        "Valor",
        places=2,
        rounding=ROUND_HALF_UP,
        validators=[DataRequired(message="Informe o valor."), NumberRange(min=0.01, message="Valor deve ser maior que 0.")],
    )
    submit = SubmitField("Salvar")


class DeleteForm(FlaskForm):
    """Formulário mínimo só para CSRF no botão Excluir."""
    submit = SubmitField("Excluir")
