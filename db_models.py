import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

SECRET_KEY = '1a0b329df51147t0va111335d2acbfd8'
app.config['SECRET_KEY'] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

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
