from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ArticleForm(FlaskForm):
    code = IntegerField("Code", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField("Unit Price", validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField("Add Article")
