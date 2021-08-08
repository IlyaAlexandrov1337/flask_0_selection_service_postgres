import json
import os
import forms

from random import sample, shuffle
from flask import Flask, render_template, request, redirect
from flask_wtf.csrf import CSRFProtect
from json_operations import open_json
from flask import Flask, render_template
from sqlalchemy.sql.expression import func
from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
csrf = CSRFProtect(app)

SECRET_KEY = '1a0b329df51147t0a111335d2acbfd8'
app.config['SECRET_KEY'] = SECRET_KEY
app.config["SQLALCHEMY_database_json_URI"] = os.environ.get("database_json_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница", "sat": " Суббота",
        "sun": "Воскресенье"}

goals_to_teachers_table = db.Table('goals_to_teachers',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
    db.Column('goal_id', db.String, db.ForeignKey('goals.name'))
)


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    free = db.Column(db.JSON, nullable=False)
    booking = db.relationship("Booking", back_populates="teacher")
    goals = db.relationship("Goal", secondary=goals_to_teachers_table, back_populates="teacher")


class Goal(db.Model):
    __tablename__ = 'goals'

    name = db.Column(db.String, nullable=False, primary_key=True)
    description = db.Column(db.String, nullable=False)
    teacher = db.relationship("Teacher", secondary=goals_to_teachers_table, back_populates="goals")



class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    teacher = db.relationship("Teacher", back_populates="booking")
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))


class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)

goal_obj_dict = {}
for t in open_json("database_json_json/teachers.json"):
    flag = False
    if Teacher.query.get(t['id']):
        continue
    teach_obj = Teacher(id=t['id'], name=t['name'], about=t['about'], rating=t['rating'], picture=t['picture'],
                        price=t['price'], free=json.dumps(t['free']))
    for goal in t['goals']:
        if goal not in goal_obj_dict.keys():
            goal_obj_dict[goal] = Goal(name=goal, description=open_json("database_json_json/goals.json")[goal])
            db.session.add(goal_obj_dict[goal])
        goal_obj_dict[goal].teacher.append(teach_obj)
    db.session.add(teach_obj)
    flag = True

if flag:
    db.session.commit()


@app.errorhandler(500)
def render_server_error(error):
    return f'<h1>Что-то не так, но мы все починим</h1><p>{error}</p>'


@app.errorhandler(404)
def render_server_error(error):
    return f'<h1>Ничего не нашлось! Вот неудача, url некорректный:(</h1><p>{error}</p>'


@app.route("/")
def main_render():
    six_teachers = Teacher.query.order_by(func.random()).limit(6)
    goals = Goal.query.order_by(Goal.description.desc()).all()
    return render_template('index.html', goals=goals, teachers=six_teachers)


@app.route("/all", methods=["GET", "POST"])
def all_render():
    form = forms.AllForm()
    if form.validate_on_submit() and request.method == "POST":
        target = form.options.data
    else:
        target = 'rand'
    if target == 'rand':
        teachers_sorted = Teacher.query.order_by(func.random()).all()
    elif target == 'best_rat':
        teachers_sorted = Teacher.query.order_by(Teacher.rating.desc()).all()
    elif target == 'more_price':
        teachers_sorted = Teacher.query.order_by(Teacher.price.desc()).all()
    else:
        teachers_sorted = Teacher.query.order_by(Teacher.price).all()
    return render_template("all.html", form=form, teachers=teachers_sorted)


@app.route("/goals/<goal>/")
def goal_render(goal):
    print(Teacher.query.first().goals[1].name)
    goal_teachers = Teacher.query.filter(Teacher.goals.any(Goal.name == goal)).order_by(Teacher.rating.desc()).all()
    goal_descr = Goal.query.filter(Goal.name == goal).first().description
    return render_template('goal.html', teachers=goal_teachers, goal=goal_descr)


@app.route("/profiles/<int:id>/")
def profile_render(id):
    teacher = Teacher.query.get_or_404(id)
    free = json.loads(teacher.free)
    return render_template('profile.html', teacher=teacher, free=free, days=days)


@app.route("/request/", methods=["GET", "POST"])
def request_render():
    form = forms.RequestForm()
    if form.validate_on_submit() and request.method == "POST":
        goal = form.goals.data
        goals_choices = dict(form.goals.choices)
        goal_label = goals_choices[goal]
        time = form.times.data
        times_choices = dict(form.times.choices)
        time_label = times_choices[time]
        name = form.clientName.data
        phone = form.clientPhone.data
        req = Request(goal=goal_label, time=time_label, name=name, phone=phone)
        db.session.add(req)
        db.session.commit()
        return render_template('request_done.html', req=Request.query.order_by(Request.id.desc()).first())
    else:
        return render_template('request.html', form=form)


@app.route("/booking/<int:id>/<day>/<time>/", methods=["GET", "POST"])
def booking_render(id, day, time):
    form = forms.BookingForm()
    if form.validate_on_submit() and request.method == "POST":
        day = form.clientWeekday.data
        time = form.clientTime.data
        name = form.clientName.data
        phone = form.clientPhone.data
        teacher = form.clientTeacher.data
        booking = Booking(day=day, time=time, name=name, phone=phone,
                          teacher_id=Teacher.query.filter(Teacher.name == teacher).first().id)
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_done.html', book=Booking.query.order_by(Booking.id.desc()).first(), days=days)
    else:
        return render_template('booking.html', form=form, teacher=Teacher.query.get(id), day=day, time=time, days=days)


# @app.route("/booking_done/", methods=["GET", "POST"])
# def booking_done_render():
#     form = forms.BookingForm()
#     if form.validate_on_submit() and request.method == "POST":
#         data = {}
#         data['day'] = form.clientWeekday.data
#         data['time'] = form.clientTime.data
#         data['name'] = form.clientName.data
#         data['phone'] = form.clientPhone.data
#         data['teacher'] = form.clientTeacher.data
#         data_booking.append(data)
#         add_info("database_json_json/booking.json", data_booking)
#         return render_template('booking_done.html', day=data['day'], time=data['time'],
#                                name=data['name'], phone=data['phone'], days=days)
#     else:
#         redirect('/')


if __name__ == "__main__":
    app.run()
