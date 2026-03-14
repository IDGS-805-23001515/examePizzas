from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectMultipleField, IntegerField, widgets
from wtforms.validators import DataRequired, NumberRange
from wtforms.fields import DateField


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class PizzaForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    direccion = StringField("Dirección", validators=[DataRequired()])
    telefono = StringField("Teléfono", validators=[DataRequired()])

    tamano = RadioField(
        "Tamaño Pizza",
        choices=[
            ("Chica", "Chica $40"),
            ("Mediana", "Mediana $80"),
            ("Grande", "Grande $120")
        ],
        validators=[DataRequired()]
    )

    fecha = DateField(
    "Fecha del pedido",
    format="%Y-%m-%d",
    validators=[DataRequired()]
)

    ingredientes = MultiCheckboxField(
        "Ingredientes",
        choices=[
            ("Jamon", "Jamón $10"),
            ("Pina", "Piña $10"),
            ("Champinones", "Champiñones $10")
        ]
    )

    cantidad = IntegerField(
        "Núm. de Pizzas",
        validators=[DataRequired(), NumberRange(min=1)]
    )