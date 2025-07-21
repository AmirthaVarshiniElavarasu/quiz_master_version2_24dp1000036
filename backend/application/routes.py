from flask import Blueprint,jsonify,request,make_response
from flask_security import auth_required,roles_required,current_user,utils,auth_token_required
from .database import db
from .userdb import datastore
from .models import Subject,Chapter,Quiz,Questions,Option,Scores
from datetime import datetime
from flask_restful import Resource,reqparse


# subject
subject_parser = reqparse.RequestParser()
subject_parser.add_argument('sub_name', type=str, required=True, help='Subject name is required')
subject_parser.add_argument('sub_Description', type=str)

# chapter
chapter_parser = reqparse.RequestParser()
chapter_parser.add_argument('chap_title', type=str, required=True, help="Chapter title is required")
chapter_parser.add_argument('chap_description', type=str)
chapter_parser.add_argument('sub_id', type=int, required=True, help="Subject ID is required")

# quiz
quiz_parser = reqparse.RequestParser()
quiz_parser.add_argument('chap_id', type=int, required=True, help='Chapter ID is required')
quiz_parser.add_argument('quiz_date', type=str, required=True, help='Quiz date is required')
quiz_parser.add_argument('quiz_duration_hours', type=int, required=True, help='Duration hours required')
quiz_parser.add_argument('quiz_duration_minute', type=int, required=True, help='Duration minutes required')

# questions
question_parser = reqparse.RequestParser()
question_parser.add_argument('ques_statement', type=str, required=True, help="Question statement is required")
question_parser.add_argument('correct_option_id', type=int, required=True, help="Correct option is required")
question_parser.add_argument('quiz_id', type=int, required=True, help="Quiz ID is required")
question_parser.add_argument('options', type=list, location='json', required=True, help="Options are required")

main_routes=Blueprint('main_routes',__name__)

def roles_list(roles):
    role_list=[]
    for role in roles:
        role_list.append(role.name)
    return role_list

class AdminHome(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        user = current_user
    
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizzes = Quiz.query.all()

        return {
            'subjects': [s.serialize() for s in subjects],
            'chapters': [c.serialize() for c in chapters],
            'quizzes': [q.serialize() for q in quizzes],
            'user': user.username
        }
    
class UserHome(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self):
        user = current_user

        quizzes=Quiz.query.all()
        chapters=Chapter.query.all()
        subjects=Subject.query.all()

        return {
            'username':user.username,
            'subjects': [s.serialize() for s in subjects],
            'chapters': [c.serialize() for c in chapters],
            'quizzes': [q.serialize() for q in quizzes],
            
        },200


class Registration(Resource):
    def post(self):
        details_of_user=request.get_json()

        if 'email' not in details_of_user or 'password' not in details_of_user:
            return make_response(jsonify({
                'message': 'email and passwrod are required'
            }),400)
        
        email= details_of_user.get('email')
        password=utils.hash_password(details_of_user.get('password'))
        username=details_of_user.get('username')
        qualification=details_of_user.get('qualification')
        gender=details_of_user.get('gender')
        dob_str=details_of_user.get('dob')
        dob=datetime.strptime(dob_str,'%Y-%m-%d').date()

        user=datastore.find_user(email=email)
        if user:
            return make_response(jsonify({
                'message': 'User already exists'
            }),400)
        
        user_role=datastore.find_role('user')
        user=datastore.create_user(email=email,
                                password=password,
                                username=username,
                                qualification=qualification,
                                gender=gender,
                                dob=dob,
                                roles=[user_role])
        
        db.session.commit()

        return {
            'message': 'User created successfully',
            'user':{
                'email': user.email,
                'roles': [role.name for role in user.roles]
            }
        }, 201


class Login(Resource):
    def post(self):
        login_credentials = request.get_json()

        if 'email' not in login_credentials or 'password' not in login_credentials:
            return make_response(jsonify({
                'message': 'email and password are required'
            }),400)
        
        email= login_credentials.get('email')
        password= login_credentials.get('password')

        user = datastore.find_user(email=email)
        if not user:
            return make_response(jsonify({
                'message':'User does not exist'
            }),404)
        
        if not utils.verify_password(password,user.password):
            return make_response(jsonify({
                'message': 'Invalid password'
            }),401)
        utils.login_user(user)

        auth_token=user.get_auth_token()

        return {
            'message':'Login Successfully',
            'user':{
                'email': user.email,
                'roles':[role.name for role in user.roles] 
            },
            'auth_token':auth_token
        },200

class Logout(Resource):
    @auth_token_required
    def post(self):
        utils.logout_user()
        return {
            'message':'Logout successful'
        },200

class SubjectResource(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self, sub_id=None):
        if sub_id:
            subjects = Chapter.query.get_or_404(sub_id)
            return subjects.serialize(), 200
       
        subjects = Subject.query.all()
        return [ s.serialize() for s in subjects]

    @auth_token_required
    @roles_required('admin')
    def post(self):
        
        args = subject_parser.parse_args()
        if Subject.query.filter_by(sub_name=args['sub_name']).first():
            return {'message': 'Subject already exists'}, 400

        new_sub = Subject(
            sub_name=args['sub_name'],
            sub_Description=args['sub_Description'],
        )
        db.session.add(new_sub)
        db.session.commit()
        return {'message': f'Subject {new_sub.sub_name} created successfully'}, 201

    @auth_token_required
    @roles_required('admin')
    def put(self,sub_id):
        
        subject=Subject.query.get_or_404(sub_id)
        args = subject_parser.parse_args()

        subject.sub_name = args['sub_name']
        subject.sub_Description = args['sub_Description']
        db.session.commit()

        return {'message': f'Subject {subject.sub_name} updated successfully'}, 200

    @auth_token_required
    @roles_required('admin')
    def delete(self,sub_id):
        
        subject=Subject.query.get_or_404(sub_id)
       
        if subject.sub_chap:
            return {'message': 'Please delete the chapters first'}, 400

        db.session.delete(subject)
        db.session.commit()
        return {'message': f'Subject {subject.sub_name} deleted successfully'}, 200



class ChapterResource(Resource):
    # GET: Get all chapters or one chapter by id
    @auth_token_required
    @roles_required('admin')
    def get(self, chap_id=None):

        if chap_id:
            chapter = Chapter.query.get_or_404(chap_id)
            return chapter.serialize(), 200

        chapters = Chapter.query.all()
        return [c.serialize() for c in chapters], 200

    # POST: Create a new chapter
    @auth_token_required
    @roles_required('admin')
    def post(self):
        args = chapter_parser.parse_args()
        existing = Chapter.query.filter_by(chap_title=args['chap_title']).first()
        if existing:
            return {"message": "Chapter already exists"}, 400

        new_chap = Chapter(
            chap_title=args['chap_title'],
            chap_description=args['chap_description'],
            sub_id=args['sub_id']
        )
        db.session.add(new_chap)
        db.session.commit()
        return {"message": f"Chapter '{new_chap.chap_title} 'created successfully"}, 201
   
    # PUT: Update a chapter
    @auth_token_required
    @roles_required('admin')
    def put(self, chap_id):

        chapter = Chapter.query.get_or_404(chap_id)
        args = chapter_parser.parse_args()

        chapter.chap_title = args['chap_title']
        chapter.chap_description = args['chap_description']
        chapter.sub_id = args['sub_id']
        db.session.commit()

        return {"message": f"Chapter '{chapter.chap_title} 'updated successfully"}, 200

    # DELETE: Delete a chapter
    @auth_token_required
    @roles_required('admin')
    def delete(self, chap_id):
        chapter = Chapter.query.get_or_404(chap_id)
        if chapter.chap_quiz:
            return {"message": "Please delete the quizzes under this chapter first"}, 400

        db.session.delete(chapter)
        db.session.commit()
        return {"message": f"Chapter '{chapter.chap_title}' deleted successfully"}, 200



class QuizResource(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self, quiz_id=None):
        if quiz_id:
            quiz = Quiz.query.get_or_404(quiz_id)
            return quiz.serialize(), 200
        else:
            quizzes = Quiz.query.order_by(Quiz.quiz_id.desc()).all()
            quiz_list = [q.serialize() for q in quizzes]

           
            
            return {
                 'quizzes': quiz_list,
                 }, 200

    @auth_token_required
    @roles_required('admin')
    def post(self):
        args = quiz_parser.parse_args()
        latest_quiz = Quiz.query.order_by(Quiz.quiz_id.desc()).first()
        next_number = latest_quiz.quiz_id + 1 if latest_quiz else 1
        quiz_title = f"Quiz {next_number}"

        try:
            quiz_date = datetime.strptime(args['quiz_date'], '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400

        duration = (args['quiz_duration_hours'] * 60) + args['quiz_duration_minute']
        new_quiz = Quiz(
            quiz_title=quiz_title,
            chap_id=args['chap_id'],
            quiz_date=quiz_date,
            quiz_time=duration
        )
        db.session.add(new_quiz)
        db.session.commit()
        return {'message': f"{quiz_title} created successfully."}, 201

    @auth_token_required
    @roles_required('admin')
    def put(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        args = quiz_parser.parse_args()

        try:
            quiz_date = datetime.strptime(args['quiz_date'], '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400

        quiz.chap_id = args['chap_id']
        quiz.quiz_date = quiz_date
        quiz.quiz_time = (args['quiz_duration_hours'] * 60) + args['quiz_duration_minute']
        db.session.commit()

        return {'message': f"{quiz.quiz_title} updated successfully."}, 200
    
    @auth_token_required
    @roles_required('admin')
    def delete(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        if quiz.quiz_ques:
            return {'message': 'Please delete quiz questions first.'}, 400
        db.session.delete(quiz)
        db.session.commit()
        return {'message': f"{quiz.quiz_title} deleted successfully."}, 200

class QuestionResource(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self, question_id=None):
        if question_id:
           question = Questions.query.get_or_404(question_id)
           return question.serialize(), 200
        else:
            questions = Questions.query.all()
            return [q.serialize() for q in questions], 200

        
    @auth_token_required
    @roles_required('admin')
    def post(self):
        args = question_parser.parse_args()
        question = Questions(
            ques_statement=args['ques_statement'],
            correct_option_id=args['correct_option_id'],
            quiz_id=args['quiz_id']
        )
        db.session.add(question)
        db.session.flush()  # Get question ID before commit

        for opt_text in args['options']:
            option = Option(op_statement=opt_text, op_ques_id=question.ques_id)
            db.session.add(option)

        db.session.commit()
        return {"message": "Question created successfully", "question_id": question.ques_id}, 201

    @auth_token_required
    @roles_required('admin')
    def put(self, question_id):
        question = Questions.query.get_or_404(question_id)
        args = question_parser.parse_args()
        
        question.ques_statement = args['ques_statement']
        question.correct_option_id = args['correct_option_id']
        question.quiz_id = args['quiz_id']

        # Update options
        new_options = set(args['options'])
        old_options = {opt.op_statement: opt for opt in question.options}

        # Delete removed
        for old_opt_text, old_opt_obj in old_options.items():
            if old_opt_text not in new_options:
                db.session.delete(old_opt_obj)

        # Add new
        for new_opt_text in new_options:
            if new_opt_text not in old_options:
                new_option = Option(op_statement=new_opt_text, op_ques_id=question.ques_id)
                db.session.add(new_option)

        db.session.commit()
        return {"message": "Question updated successfully"}, 200

    @auth_token_required
    @roles_required('admin')
    def delete(self, question_id):
        question = Questions.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        return {"message": "Question deleted successfully"}, 200

def register_routes(api):
    api.add_resource(AdminHome,'/api/admin_dashboard')
    api.add_resource(UserHome,'/api/user_dashboard')
    api.add_resource(Registration,'/api/registration')
    api.add_resource(Login,'/api/login')
    api.add_resource(Logout, '/api/logout')
    api.add_resource(SubjectResource, '/api/admin/subject','/api/admin/subject/<int:sub_id>')
    api.add_resource(ChapterResource,'/api/chapters','/api/chapters/<int:chap_id>')
    api.add_resource(QuizResource,'/api/quizzes','/api/quizzes/<int:quiz_id>')
    api.add_resource(QuestionResource,'/api/questions','/api/questions/<int:question_id>')
