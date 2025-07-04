from .database import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime, date

class User(db.Model, UserMixin):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(150),nullable=False,unique=True)
    password=db.Column(db.String(200),nullable=False)
    fs_uniquifier=db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    username=db.Column(db.String(50),nullable=False)
    qualification=db.Column(db.String(150),nullable=False)
    gender=db.Column(db.String(6),nullable=False)
    dob=db.Column(db.Date,nullable=False)
    scores=db.relationship('Scores',backref='User',lazy=True)
    roles = db.relationship('Role',secondary='users_roles',backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    __tablename__='role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)

class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id',ondelete='CASCADE'))


class Subject(db.Model):
    __tablename__='sub'
    sub_id=db.Column(db.Integer,primary_key=True)
    sub_name=db.Column(db.String(50),nullable=False,unique=True)
    sub_Description=db.Column(db.Text,nullable=True)
    sub_quiz_descrip=db.Column(db.Text,nullable=True)
    sub_chap=db.relationship('Chapter',backref='Subject',lazy=True)
    
class Chapter(db.Model):
    __tablename__='chap'
    chap_id=db.Column(db.Integer,primary_key=True)
    chap_title=db.Column(db.String(200),nullable=False)
    chap_description=db.Column(db.Text,nullable=False)
    chap_quiz=db.relationship('Quiz',backref='Chapter',lazy=True)
    sub_id=db.Column(db.Integer,db.ForeignKey('sub.sub_id'),nullable=False)

class Quiz(db.Model):
    __tablename__='quizzes'
    quiz_id=db.Column(db.Integer,primary_key=True)
    quiz_title=db.Column(db.String(200),nullable=False)
    chap_id=db.Column(db.Integer,db.ForeignKey('chap.chap_id'),nullable=False)
    quiz_date=db.Column(db.Date,nullable=False)
    quiz_time=db.Column(db.Integer,nullable=False)
    quiz_score=db.relationship('Scores',backref='Quiz',lazy=True)
    quiz_ques=db.relationship('Questions',backref='Quiz',lazy=True)
    
    
    @property
    def question(self):
        return len(self.quiz_ques)
    
class Questions(db.Model):
    __tablename__="question"
    ques_id=db.Column(db.Integer,primary_key=True)
    ques_title=db.Column(db.String(200),nullable=False)
    ques_statement=db.Column(db.Text,nullable=False,unique=True)
    options=db.relationship('Option',backref='question',cascade='all,delete-orphan',lazy='dynamic',foreign_keys='Option.op_ques_id')
    quiz_id=db.Column(db.Integer,db.ForeignKey('quizzes.quiz_id'),nullable=False)
    correct_option=db.Column(db.Integer,db.ForeignKey('options.op_id'),nullable=True)

    def __repr__(self):
        return f"<Question: {self.ques_statement}>"
    
class Option(db.Model):
    __tablename__="options"
    op_id=db.Column(db.Integer,primary_key=True)
    op_statement=db.Column(db.Text,nullable=False)
    op_ques_id=db.Column(db.Integer,db.ForeignKey('question.ques_id'),nullable=False)
   
    
    def __repr__(self):
        return f"<Option: {self.op_statement}>"


class Scores(db.Model):
    __tablename__="score"
    score_id=db.Column(db.Integer,primary_key=True)
    quiz_score_id=db.Column(db.Integer,db.ForeignKey('quizzes.quiz_id',ondelete='CASCADE'),nullable=False)
    user_score_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False)
    score_time_stamp=db.Column(db.DateTime,nullable=False)
    score_total=db.Column(db.Integer,nullable=False)
    No_of_question=db.Column(db.Integer,nullable=False)
