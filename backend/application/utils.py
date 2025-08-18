from .database import db
from .models import Subject,Chapter,Quiz,Scores
from jinja2 import Template
import random




def generate_color():
    return "#{:06x}".format(random.randint(0,0XFFFFFF))

def get_user_attempts_by_subject():
    user_attempts = (
        db.session.query(
            Subject.sub_name,
            db.func.count(db.func.distinct(Scores.user_score_id)).label("user_attempts")  # Unique users per subject
        )
        .join(Chapter, Subject.sub_id == Chapter.sub_id)
        .join(Quiz, Chapter.chap_id == Quiz.chap_id)
        .join(Scores, Quiz.quiz_id == Scores.quiz_score_id)
        .group_by(Subject.sub_name)
        .all()
    )
    return user_attempts

def get_total_scores_by_subject():
    total_scores = (
        db.session.query(Subject.sub_name,db.func.max(Scores.score_total).label("total_score"))
        .join(Chapter, Subject.sub_id == Chapter.sub_id)
        .join(Quiz, Chapter.chap_id == Quiz.chap_id)
        .join(Scores, Quiz.quiz_id == Scores.quiz_score_id)
        .group_by(Subject.sub_name)
        .all()
    )
    return total_scores

def get_no_of_subject_by_quiz(user_id):
    Quiz_subjects=(
        db.session.query(
            Subject.sub_name,
            db.func.count(db.func.distinct(Scores.quiz_score_id)).label("no_of_quiz")  # Unique quiz per subject
        )
        .join(Chapter, Subject.sub_id == Chapter.sub_id)
        .join(Quiz, Chapter.chap_id == Quiz.chap_id)
        .join(Scores, Quiz.quiz_id == Scores.quiz_score_id)
        .filter(Scores.user_score_id ==user_id)
        .group_by(Subject.sub_name)
        .all())
    return Quiz_subjects

def get_no_of_attempts_by_month(user_id):
    quiz_attempt=(
        db.session.query(
            db.func.extract('year',Scores.score_time_stamp).label('year'),
            db.func.extract('month',Scores.score_time_stamp).label('month'),
            db.func.count(db.func.distinct(Scores.quiz_score_id)).label("no_of_quiz"))
            .filter(Scores.user_score_id==user_id)
            .group_by('year', 'month')
            .order_by('year', 'month')
            .all())
    return quiz_attempt

def roles_list(roles):
    role_list=[]
    for role in roles:
        role_list.append(role.name)
    return role_list
