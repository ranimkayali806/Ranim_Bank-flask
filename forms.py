from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, SelectField

class WithdrawForm(FlaskForm):
      amount = IntegerField('amount', validators=[validators.DataRequired(), validators.NumberRange(min=1,max=1000000)])


class DepositeForm(FlaskForm):
      amount_2 = IntegerField('amount', validators=[validators.DataRequired(), validators.NumberRange(min=1,max=1000000)])
