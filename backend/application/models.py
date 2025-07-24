from .database import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime, date

# Association table for User-Role
class Role(db.Model, RoleMixin):
    __tablename__='role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

# Role Model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id',ondelete='CASCADE'))

# User Model
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
    
    # Relationships 
    scores=db.relationship('Scores',backref='User',lazy=True)
    roles = db.relationship('Role',secondary='users_roles',backref=db.backref('users', lazy='dynamic'))

    def serialize(self):
        return{
            'id':self.id,
            'email':self.email,
            'username':self.username,
            'qualification':self.qualification,
            'gender':self.gender,
            'dob':str(self.dob)
        }

# Subject Model
class Subject(db.Model):
    __tablename__='sub'
    sub_id=db.Column(db.Integer,primary_key=True)
    sub_name=db.Column(db.String(50),nullable=False,unique=True)
    sub_Description=db.Column(db.Text,nullable=True)


    # Relationship
    sub_chap=db.relationship('Chapter',backref='Subject',lazy=True)
    
    def serialize(self):
        return {
            'sub_id': self.sub_id,
            'sub_name': self.sub_name,
            'sub_Description':self.sub_Description,
            'sub_chap':[chapter.serialize_basic() for chapter in self.sub_chap]
         
            
        }
    
# Chapter Model    
class Chapter(db.Model):
    __tablename__='chap'
    chap_id=db.Column(db.Integer,primary_key=True)
    chap_title=db.Column(db.String(200),nullable=False)
    chap_description=db.Column(db.Text,nullable=False)
    sub_id=db.Column(db.Integer,db.ForeignKey('sub.sub_id'),nullable=False)
    
    # Relationship
    chap_quiz=db.relationship('Quiz',backref='Chapter',lazy=True)
    
    def serialize(self):
        return{
            'chap_id': self.chap_id,
            'chap_title':self.chap_title,
            'chap_description':self.chap_description,
            'sub_id':self.sub_id,
            'chap_quiz':[quiz.serialize_basic() for quiz in self.chap_quiz]
        }
    
    def serialize_basic(self):
        return{
            'chap_id':self.chap_id,
            'chap_name':self.chap_title
        } 

# Quiz Model
class Quiz(db.Model):
    __tablename__='quizzes'
    quiz_id=db.Column(db.Integer,primary_key=True)
    quiz_title=db.Column(db.String(200),nullable=False)
    quiz_description = db.Column(db.Text, nullable=True)
    quiz_date=db.Column(db.Date,nullable=False)
    quiz_time=db.Column(db.Integer,nullable=False)
    chap_id=db.Column(db.Integer,db.ForeignKey('chap.chap_id'),nullable=False)
    
    # Relationship
    quiz_score=db.relationship('Scores',backref='Quiz',lazy=True)
    quiz_ques=db.relationship('Questions',backref='Quiz',lazy=True)
    
    @property
    def total_questions(self):
        return len(self.quiz_ques)
    
    def serialize(self):
        return {
            'quiz_id': self.quiz_id,
            'quiz_title': self.quiz_title,
            'quiz_description': self.quiz_description,
            'quiz_date': self.quiz_date.strftime("%Y-%m-%d %H:%M:%S"),
            'quiz_time': self.quiz_time,
            'chap_id': self.chap_id,
            'total_questions': self.total_questions,
            'questions': [q.serialize() for q in self.quiz_ques]
        }

    def serialize_basic(self):
        return {
            'quiz_id': self.quiz_id,
            'quiz_title': self.quiz_title,
        }

# Questions Model   
class Questions(db.Model):
    __tablename__="question"
    ques_id=db.Column(db.Integer,primary_key=True)
    ques_statement=db.Column(db.Text,nullable=False,unique=True)
    quiz_id=db.Column(db.Integer,db.ForeignKey('quizzes.quiz_id'),nullable=False)
    correct_option_id=db.Column(db.Integer,db.ForeignKey('options.op_id',ondelete='SET NULL'),nullable=True)

    # Relationship
    options=db.relationship('Option',backref='question',cascade='all,delete-orphan',lazy='dynamic',foreign_keys='Option.op_ques_id')
    correct_option = db.relationship('Option', foreign_keys=[correct_option_id],passive_deletes=True)

    def serialize(self):
        return {
            'quiz_id':self.quiz_id,
            'ques_id': self.ques_id,
            'ques_statement': self.ques_statement,
            'options': [option.serialize() for option in self.options],
            'correct_option': self.correct_option.serialize() if self.correct_option else None
        } 

# Options Model  
class Option(db.Model):
    __tablename__="options"
    op_id=db.Column(db.Integer,primary_key=True)
    op_statement=db.Column(db.Text,nullable=False)
    op_ques_id=db.Column(db.Integer,db.ForeignKey('question.ques_id',ondelete="CASCADE"),nullable=False)
   
    
    def serialize(self):
        return {
            'op_id': self.op_id,
            'op_statement': self.op_statement
        }

# Scores Model 
class Scores(db.Model):
    __tablename__="score"
    score_id=db.Column(db.Integer,primary_key=True)
    score_total=db.Column(db.Integer,nullable=False)
    No_of_question=db.Column(db.Integer,nullable=False)
    score_time_stamp = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_score_id=db.Column(db.Integer,db.ForeignKey('quizzes.quiz_id',ondelete='CASCADE'),nullable=False)
    user_score_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False)

    def serialize(self):
        return {
            'score_id': self.score_id,
            'score_total': self.score_total,
            'No_of_question': self.No_of_question,
            'score_time_stamp': self.score_time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
            'username': self.user.username,
            'quiz_name': self.quiz.quiz_title
        }