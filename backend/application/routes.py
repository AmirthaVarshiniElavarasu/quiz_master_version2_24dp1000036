from flask import jsonify,request,make_response,send_from_directory
from flask_security import auth_required,roles_required,current_user,utils,auth_token_required,roles_accepted
from .database import db
from .userdb import datastore
from .models import *
from .utils import *
from datetime import datetime,timezone,time
from flask_restful import Resource,reqparse
from sqlalchemy import desc,func
import calendar
from celery.result import AsyncResult
from .tasks import csv_report,daily_reminder


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
question_parser.add_argument('correct_option_id', type=int, required=False, help="Correct option is required")
question_parser.add_argument('quiz_id', type=int, required=True, help="Quiz ID is required")
question_parser.add_argument('options', type=list, location='json', required=True, help="Options are required")
question_parser.add_argument('correct_option_index', type=int, required=True)

reminder_parser = reqparse.RequestParser()
reminder_parser.add_argument('hour', type=int, required=True)
reminder_parser.add_argument('minute', type=int, required=True)



class AdminHome(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizzes = Quiz.query.all()

        return {
            'subjects': [s.serialize() for s in subjects],
            'chapters': [c.serialize() for c in chapters],
            'quizzes': [q.serialize() for q in quizzes],
            
            
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

        # Record login time
        existing = User_login_activity.query.filter_by(username=user.username).first()
        if not existing:
            login_record = User_login_activity(username=user.username, last_login=datetime.utcnow())
            db.session.add(login_record)
        else:
            existing.last_login = datetime.utcnow()

        db.session.commit()

        return {
            'message':'Login Successfully',
            'user':{
                'email': user.email,
                'roles':[role.name for role in user.roles],
                'username' : user.username,
                'user_id': user.id
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
            subjects = Subject.query.get_or_404(sub_id)
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
            quizzes = Quiz.query.order_by(Quiz.quiz_id.asc()).all()
            chapter = Chapter.query.order_by(Chapter.chap_id.asc()).all()
            quiz_list = [q.serialize() for q in quizzes]
            chap_list = [c.serialize() for c in chapter]
            return {
                 'quizzes': quiz_list,
                 'chapters': chap_list
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
        daily_reminder.delay()
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
            quiz_id=args['quiz_id'],
            correct_option_id=None  # set later
        )
        db.session.add(question)
        db.session.flush()  # so question.ques_id is available

        option_objs = []
        for opt_text in args['options']:
            opt = Option(op_statement=opt_text, op_ques_id=question.ques_id)
            db.session.add(opt)
            option_objs.append(opt)

        db.session.flush()  # to get op_ids

        correct_index = args.get('correct_option_index')
        if correct_index is not None and 0 <= correct_index < len(option_objs):
            question.correct_option_id = option_objs[correct_index].op_id

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

class SearchResource(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'user')
    def get(self):
        query = request.args.get("q", "").strip()
        source = request.args.get("source", "").strip()

        if not query:
            return jsonify({"error": "Empty search query"}), 400

        role = "admin" if "admin" in roles_list(current_user.roles) else "user"
        user_id = current_user.id

        # Initial result containers
        user_results, quiz_results, subject_results, chapter_results, scores_results = [], [], [], [], []
        users, subjects, quizzes, chapters, scores = [], [], [], [], []

        if source == "admin-navbar" and role == "admin":
            if query.lower().startswith("user"):
                users = User.query.all()
            if query.lower().startswith("subject"):
                subjects = Subject.query.all()
            if query.lower().startswith("quiz"):
                quizzes = Quiz.query.all()
            if query.lower().startswith("chapter"):
                chapters = Chapter.query.all()
            if query.lower().startswith("score"):
                scores = Scores.query.all()

            user_results = User.query.filter(
                User.id.like(f"%{query}%") |
                User.username.ilike(f"%{query}%") |
                User.gender.ilike(f"%{query}%") |
                User.email.ilike(f"%{query}%")
            ).all()

            quiz_results = Quiz.query.filter(
                Quiz.quiz_id.like(f"%{query}%") |
                Quiz.quiz_title.ilike(f"%{query}%")
            ).all()

            subject_results = Subject.query.filter(
                Subject.sub_id.like(f"%{query}%") |
                Subject.sub_name.ilike(f"%{query}%")
            ).all()

            chapter_results = Chapter.query.filter(
                Chapter.chap_id.like(f"%{query}%") |
                Chapter.chap_title.ilike(f"%{query}%")
            ).all()

        elif source == "user-navbar" and role == "user":
            if query.lower().startswith("subject"):
                subjects = Subject.query.all()
            if query.lower().startswith("quiz"):
                quizzes = Quiz.query.all()
            if query.lower().startswith("chapter"):
                chapters = Chapter.query.all()
            if query.lower().startswith("score"):
                scores = Scores.query.filter_by(user_score_id=user_id).all()

            quiz_results = Quiz.query.filter(
                Quiz.quiz_id.like(f"%{query}%") |
                Quiz.quiz_title.ilike(f"%{query}%")
            ).all()

            subject_results = Subject.query.filter(
                Subject.sub_id.like(f"%{query}%") |
                Subject.sub_name.ilike(f"%{query}%")
            ).all()

            chapter_results = Chapter.query.filter(
                Chapter.chap_id.like(f"%{query}%") |
                Chapter.chap_title.ilike(f"%{query}%")
            ).all()

            scores_results = Scores.query.filter(
                Scores.user_score_id == user_id,
                (Scores.quiz_score_id.like(f"%{query}%") |
                 Scores.score_total.like(f"%{query}%"))
            ).all()

        results = {
            "Users": [{
                "Id": u.id,
                "Username": u.username,
                "Email": u.email,
                "Qualification": u.qualification,
                "Gender": u.gender,
                "Date_of_Birth": u.dob.strftime('%d-%m-%Y')
            } for u in users],
            "Subjects": [{
                "Subject_Id": s.sub_id,
                "Subject_Name": s.sub_name
            } for s in subjects],
            "Quizzes": [{
                "Quiz_Id": q.quiz_id,
                "Quiz_Title": q.quiz_title,
                "Quiz_Chapter_Id": q.chap_id,
                "Quiz_Start_Date": q.quiz_date,
                "Quiz_Duration": q.quiz_time
            } for q in quizzes],
            "Chapters": [{
                "Chapter_Id": c.chap_id,
                "Chapter_Title": c.chap_title
            } for c in chapters],
            "Scores": [{
                "User_Id": sc.user_score_id,
                "Quiz_Id": sc.quiz_score_id,
                "score_id": sc.score_id,
                "Total_Score": sc.score_total
            } for sc in scores],
            "User": [{
                "Id": u.id,
                "Username": u.username,
                "Email": u.email,
                "Qualification": u.qualification,
                "Gender": u.gender,
                "Date_of_Birth": u.dob.strftime('%d-%m-%Y')
            } for u in user_results],
            "Quiz": [{
                "Quiz_Id": q.quiz_id,
                "Quiz_Title": q.quiz_title,
                "Quiz_Chapter_Id": q.chap_id,
                "Quiz_Start_Date": q.quiz_date,
                "Quiz_Duration": q.quiz_time
            } for q in quiz_results],
            "Subject": [{
                "Subject_Id": s.sub_id,
                "Subject_Name": s.sub_name
            } for s in subject_results],
            "Chapter": [{
                "Chapter_Id": c.chap_id,
                "Chapter_Title": c.chap_title
            } for c in chapter_results],
            "Score": [{
                "Quiz_Id": sc.quiz_score_id,
                "score_id": sc.score_id,
                "Total_Score": sc.score_total
            } for sc in scores_results]
        }

        return jsonify(results)

class Quizview(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    def get(self, sub_id, chap_id):
        # Logic to fetch and return quiz view data
        subject = Subject.query.get_or_404(sub_id)
        chapter = Chapter.query.get_or_404(chap_id)
       
        
        if not subject or not chapter:
            return {'error': 'Subject or Chapter not found'}, 404

        return {
            'subject': {
                'sub_id': subject.sub_id,
                'sub_name': subject.sub_name,
                'sub_Description':subject.sub_Description,
            },
            'chapter': {
                'chap_id': chapter.chap_id,
                'chap_title': chapter.chap_title,
                'chap_description':chapter.chap_description,
            }
        }, 200

class QuestionsPage(Resource):
    @auth_required('token')
    @roles_accepted('admin','user')
    def get(self, quiz_id):
        user=current_user
        quizzes = Quiz.query.get_or_404(quiz_id)
        questions = Questions.query.filter_by(quiz_id=quiz_id).all()
        if not questions:
            return {'error': 'Questions not found'}, 404
        
        return {
            'questions': [q.serialize() for q in questions],
            'quizzes' : quizzes.serialize(),
            'user': user.serialize()
        }, 200
    
class QuizSubmission(Resource):
    @auth_required('token')
    @roles_required('user')
    def post(self, quiz_id):
        
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Questions.query.filter_by(quiz_id=quiz_id).all()

        correctAnswer = {str(q.ques_id): q.correct_option for q in questions}
        No_of_quest = len(quiz.quiz_ques)

        userAnswers = request.get_json()
        if not userAnswers:
            total=0

        total = 0
        for ques_id, correct_ans in correctAnswer.items():
            if ques_id not in userAnswers:
                userAnswers[ques_id] = "none"
            if userAnswers[ques_id] == correct_ans.op_statement:
                total += 1

        time = datetime.now(timezone.utc)
        new_score = Scores(
            quiz_score_id=quiz_id,
            user_score_id=current_user.id,
            score_time_stamp=time,
            score_total=total,
            No_of_question=No_of_quest
        )
        db.session.add(new_score)
        db.session.commit()

        return {
            "message": "Quiz submitted successfully",
            "quiz_id": quiz_id,
            "data": userAnswers,
            "score": {
                "score_total": total,
                "No_of_question": No_of_quest,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            
        }, 200

class ScorePage(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'user')
    def get(self, user_id=None):
        if user_id:
            scores = Scores.query.filter_by(user_score_id=user_id)\
                                 .order_by(desc(Scores.score_total))\
                                 .limit(10).all()
            return [s.serialize() for s in scores], 200
        else:
            return {'message': 'User ID is required'}, 400

class SummaryDashboard(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'user')
    def get(self):
        user_role = roles_list(current_user.roles)

        def get_leaderboard(role_name):
            top_users = (
                db.session.query(
                    User.id,
                    User.username,
                    func.sum(Scores.score_total).label('total_score')
                )
                .join(Scores, Scores.user_score_id == User.id)
                .join(User.roles)
                .filter(Role.name == role_name)
                .group_by(User.id)
                .order_by(desc('total_score'))
                .limit(10)
                .all()
            )
            return [
                {"id": user.id, "username": user.username, "total_score": int(user.total_score)}
                for user in top_users
            ]

        if 'admin' in user_role:
            # Admin summary
            users = User.query.all()
            total_scores = Scores.query.all()
            subject_scores = get_total_scores_by_subject()
            subject_attempt = get_user_attempts_by_subject()

            bar_data = [
                {"subject": subject, "score": score, "color": generate_color()}
                for subject, score in subject_scores
            ]
            pie_data = [
                {"subject": subject, "attempts": attempts, "color": generate_color()}
                for subject, attempts in subject_attempt
            ]
            leaderboard = get_leaderboard('user')  # Admin sees leaderboard of users

            return jsonify({
                "role": "admin",
                "total_users": len(users),
                "total_scores": len(total_scores),
                "bar_data": bar_data,
                "pie_data": pie_data,
                "leaderboard": leaderboard
            })

        else:
            # User summary
            user_id = current_user.id
            subject_scores = get_no_of_subject_by_quiz(user_id)
            quiz_attempts = get_no_of_attempts_by_month(user_id)

            bar_data = [
                {"subject": subject, "attempts": attempts, "color": generate_color()}
                for subject, attempts in subject_scores
            ]
            pie_data = [
                {
                    "month": f"{calendar.month_name[month]} {year}",
                    "attempts": attempts,
                    "color": generate_color()
                }
                for year, month, attempts in quiz_attempts
            ]
            leaderboard = get_leaderboard('user')  # Users also see top user scores

            return jsonify({
                "role": "user",
                "bar_data": bar_data,
                "pie_data": pie_data,
                "leaderboard": leaderboard
            })

class ExportCSVReport(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        result= csv_report.delay()
        return jsonify({
            "id" : result.id,
            "result": result.result,
        })

class CsvResult(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self,id):
        result = AsyncResult(id)
        return send_from_directory("csv_files", result.result)

class UpdateReminderTime(Resource):
    @auth_token_required
    def put(self):
        args = reminder_parser.parse_args()
        user_id = current_user.id
        user = User.query.get_or_404(user_id)

        try:
            reminder_time = time(args['hour'], args['minute'])
        except ValueError:
            return {'message': 'Invalid time format'}, 400

        user.reminder_time = reminder_time
        db.session.commit()

        return {'message': f'Reminder time set to {reminder_time.strftime("%H:%M")}'}, 200

def register_routes(api):
    api.add_resource(AdminHome,'/api/admin_dashboard')
    api.add_resource(UserHome,'/api/user_dashboard')
    api.add_resource(Registration,'/api/registration')
    api.add_resource(Login,'/api/login')
    api.add_resource(Logout, '/api/logout')
    api.add_resource(SubjectResource, '/api/subject','/api/subject/<int:sub_id>')
    api.add_resource(ChapterResource,'/api/chapters','/api/chapters/<int:chap_id>')
    api.add_resource(QuizResource,'/api/quizzes','/api/quizzes/<int:quiz_id>')
    api.add_resource(QuestionResource,'/api/questions','/api/questions/<int:question_id>')
    api.add_resource(SearchResource, '/api/search')
    api.add_resource(Quizview, '/api/quizview/<int:sub_id>/<int:chap_id>')
    api.add_resource(QuestionsPage,'/api/questions_page/<int:quiz_id>')
    api.add_resource(QuizSubmission,'/api/quiz_submission/<int:quiz_id>')
    api.add_resource(ScorePage,'/api/score_page/<int:user_id>')
    api.add_resource(SummaryDashboard,'/api/summary_page')
    api.add_resource(ExportCSVReport,'/api/export_csv')
    api.add_resource(CsvResult,'/api/csv_result/<string:id>')
    api.add_resource(UpdateReminderTime, '/api/user/reminder-time')



