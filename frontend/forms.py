from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired, ValidationError
from front import get_nodes


class Insert(FlaskForm):
    key = StringField('key', validators=[DataRequired()])
    value = StringField('value', validators=[DataRequired()])
    nodes = IntegerField('Node', validators=[InputRequired(), get_nodes, NumberRange(min=0)], default=0)


class Delete(FlaskForm):
    key = StringField('key', validators=[DataRequired()])
    nodes = IntegerField('Node', validators=[InputRequired(), get_nodes, NumberRange(min=0)], default=0)


class Query(FlaskForm):
    key = StringField('key', validators=[DataRequired()], default="*")
    nodes = IntegerField('Node', validators=[InputRequired(), get_nodes, NumberRange(min=0)], default=0)


class Depart(FlaskForm):
    nodes = IntegerField('Node', validators=[InputRequired(), get_nodes, NumberRange(min=1)])


class Reset(FlaskForm):
    ks = ['1', '3', '5']
    k = SelectField('Replication k', choices=ks, validators=[DataRequired()])
    line = ['Linearization', 'Eventual']
    Linearization = SelectField('Consistency', choices=line, validators=[DataRequired()])
