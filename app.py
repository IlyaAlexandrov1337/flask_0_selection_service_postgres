import json
import forms

from db_models import Teacher, Goal, Booking, Request, app, db
from flask import Flask, render_template, request, redirect
from flask_wtf.csrf import CSRFProtect
from json_operations import open_json
from flask import Flask, render_template
from sqlalchemy.sql.expression import func


csrf = CSRFProtect(app)


days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница", "sat": " Суббота",
        "sun": "Воскресенье"}


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
    goal = Goal.query.filter(Goal.name == goal).first()
    if not goal:
            return redirect('/')
    goal_teachers = Teacher.query.filter(Teacher.goals.any(Goal.name == goal.name)).order_by(Teacher.rating.desc()).all()
    goal_descr = Goal.query.filter(Goal.name == goal.name).first().description
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


if __name__ == "__main__":
        
    goal_obj_dict = {}
    for t in open_json("database_json/teachers.json"):
        flag = False
        if Teacher.query.get(t['id']):
            continue
        teach_obj = Teacher(id=t['id'], name=t['name'], about=t['about'], rating=t['rating'], picture=t['picture'],
                            price=t['price'], free=json.dumps(t['free']))
        for goal in t['goals']:
            if goal not in goal_obj_dict.keys():
                goal_obj_dict[goal] = Goal(name=goal, description=open_json("database_json/goals.json")[goal])
                db.session.add(goal_obj_dict[goal])
            goal_obj_dict[goal].teacher.append(teach_obj)
        db.session.add(teach_obj)
        flag = True

    if flag:
        db.session.commit()

    app.run()
