from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Regexp, NumberRange


class CasesForm(FlaskForm):

    datestamp = StringField(u'datestamp',
                            validators=[
                                DataRequired(
                                    message="enter date/time in 24hr format MM/DD/YYYY HH:MM")
                            ])

    # NB IntegerField() would not accept 0 as input!!
    # NumberRange is not working the way I expect

    new_cases = StringField(u'new_cases', default="0", validators=[
        DataRequired(message="enter new cases"),
        #        NumberRange(min=0, max=1000, message="'cases' is out of range")
    ])

    total_cases = StringField(u'total_cases', default="0", validators=[
        DataRequired(message="enter total cases"),
        #        NumberRange(min=0, max=10000, message="'cases' is out of range")
    ])

    negative = StringField(u'negative', default="0",  validators=[
        DataRequired(message="enter negative tests"),
        #        NumberRange(min=0, max=100000, message="'negative' is out of range")
    ])

    new_deaths = StringField(u'new_deaths', default="0", validators=[
        DataRequired(message="enter new deaths"),
        #        NumberRange(min=0, max=100, message="'new deaths' is out of range")
    ])

    total_deaths = StringField(u'total_deaths', default="0", validators=[
        DataRequired(message="enter total deaths"),
        #        NumberRange(min=0, max=10000, message="'total deaths' is out of range")
    ])

    submit = SubmitField(u"Submit")


# That's all!
