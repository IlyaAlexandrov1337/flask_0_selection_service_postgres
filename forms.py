from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, RadioField, SelectField
from wtforms.validators import InputRequired


class BookingForm(FlaskForm):
    clientWeekday = HiddenField()
    clientTime = HiddenField()
    clientTeacher = HiddenField()
    clientName = StringField('Вас зовут', [InputRequired(message="Введите что-нибудь")])
    clientPhone = StringField('Ваш телефон', [InputRequired(message="Введите что-нибудь")])
    submit = SubmitField("Записаться на пробный урок")


class RequestForm(FlaskForm):
    goals = RadioField('Какая цель занятий?', choices=[("travel", "Для путешествий"), ("study", "Для школы"),
                                                      ("work", "Для работы"), ("relocate", "Для переезда"),
                                                       ("programming", "Для программирования")],
                       default="Для путешествий")
    times = RadioField('Сколько времени есть?', choices=[("1-2", "1-2 часа в неделю"),
                                                         ("3-5", "3-5 часов в неделю"),
                                                        ("5-7", "5-7 часов в неделю"),
                                                         ("7-10", "7-10 часов в неделю")],
                       default="5-7 часов в неделю")
    clientName = StringField('Вас зовут', [InputRequired(message="Введите что-нибудь")])
    clientPhone = StringField('Ваш телефон', [InputRequired(message="Введите что-нибудь")])
    submit = SubmitField("Записаться на пробный урок")


class AllForm(FlaskForm):
    options = RadioField('options', choices=[('rand', 'В случайном порядке'),
                                                ('best_rat', 'Сначала лучшие по рейтингу'),
                                                ('more_price', 'Сначала дорогие'),('less_price', 'Сначала недорогие')])
    submit = SubmitField("Сортировать")
