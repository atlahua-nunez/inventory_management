from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField
from wtforms.validators import DataRequired, URL, Email, NumberRange
from flask_ckeditor import CKEditorField

class ArticleForm(FlaskForm):
    code = IntegerField("Code", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField("Unit Price", validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField("Add Article")

