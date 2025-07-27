from collections import Counter,defaultdict
from .models import User,Quiz,Scores,Chapter,User_login_activity
from sqlalchemy import extract
from sqlalchemy.orm import joinedload
from .mail import send_email
from .utils import format_report
from celery import shared_task
from datetime import datetime,timedelta
from .database import db
import csv,requests,os



@shared_task(ignore_results=False,name = "csv_report")
def csv_report():
    
    csv_filename="UserQuizDetails.csv"
    with open(f'/Source/csv_files/{csv_filename}','w',newline="") as csvfile:
        output=csv.writer(csvfile,delimiter=',')
        output.writerow([
        "s.no","user_id", "username", "quizzes_taken", "average_score (%)", "mostly_attended_subject"
    ])
        users = User.query.all()
        S_no=1
        for user in users:
            scores = Scores.query.filter_by(user_score_id=user.id).all()
            if not scores:
                continue

            quizzes_taken = len(scores)
            avg_score = sum((s.score_total / s.No_of_question) * 100 for s in scores) / quizzes_taken

        
            subject_names = []
            for s in scores:
                quiz = s.Quiz
                chapter = quiz.Chapter
                subject = chapter.Subject
                subject_names.append(subject.sub_name)

            most_common_subject = Counter(subject_names).most_common(1)
            most_attended = most_common_subject[0][0] if most_common_subject else "N/A"

            output.writerow([
                S_no,
                user.id,
                user.username,
                quizzes_taken,
                round(avg_score, 2),
                most_attended
            ])
            S_no += 1
                
    return csv_filename

@shared_task(ignore_results=False, name="monthly_report")
def monthly_report():
    now = datetime.now()


    monthly_scores = (
        db.session.query(Scores)
        .options(
            joinedload(Scores.Quiz).joinedload(Quiz.Chapter).joinedload(Chapter.Subject),
            joinedload(Scores.User)
        )
        .filter(extract('month', Scores.score_time_stamp) == now.month)
        .filter(extract('year', Scores.score_time_stamp) == now.year)
        .all()
    )


    user_score_map = defaultdict(list)
    quiz_ids = set()

    for score in monthly_scores:
        user_score_map[score.user_score_id].append(score)
        quiz_ids.add(score.quiz_score_id)


    all_quiz_scores = defaultdict(list)
    quiz_scores_query = (
        db.session.query(Scores)
        .filter(Scores.quiz_score_id.in_(quiz_ids))
        .order_by(Scores.quiz_score_id, Scores.score_total.desc())
        .all()
    )

    for s in quiz_scores_query:
        all_quiz_scores[s.quiz_score_id].append(s)


    for user_id, scores in user_score_map.items():
        user_obj = db.session.get(User, user_id)
        quizzes_data = []

        for score in scores:
            quiz = score.Quiz
            chapter = quiz.Chapter
            subject = chapter.Subject

            quiz_scores = all_quiz_scores[quiz.quiz_id]
            rank = next((i + 1 for i, s in enumerate(quiz_scores) if s.user_score_id == user_id), None)

            quizzes_data.append({
                'title': quiz.quiz_title,
                'subject': subject.sub_name,
                'date': score.score_time_stamp.strftime('%Y-%m-%d'),
                'score': score.score_total,
                'max_score': score.No_of_question,
                'rank': rank
            })

        user_data = {
            'username': user_obj.username,
            'email': user_obj.email,
            'quizzes': quizzes_data
        }

        # Render HTML email and send it
        message = format_report('Source/Mail_template.html', user_data)
        send_email(user_obj.email, subject="Monthly Quiz Performance Report - Quiz Master", message=message)

    return "Monthly quiz reports sent"




@shared_task(ignore_results=False, name="daily_reminder")
def daily_reminder():
    now = datetime.now()
    current_time = now.time()
    inactive_since = now - timedelta(minutes=2)

    quizzes_today = Quiz.query.filter(Quiz.quiz_date == now.date()).all()
    if not quizzes_today:
        return "No new quizzes today"

    users = User_login_activity.query.filter(User_login_activity.last_login < inactive_since).all()
    count = 0

    for user in users:
        if user.reminder_time:
            user_seconds = user.reminder_time.hour * 3600 + user.reminder_time.minute * 60
            now_seconds = current_time.hour * 3600 + current_time.minute * 60

            if abs(user_seconds - now_seconds) <= 600:
                message = f"Hi {user.username}, you have new quizzes! Check: http://127.0.0.1:5000"
                webhook_url = "https://chat.googleapis.com/v1/spaces/AAQAPcnFblE/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=4sYFwaJVHcOQ36zw8gp8jh8HtcA5KPu-DK4UZZ7c3xA"
                requests.post(webhook_url, json={"text": message})
                count += 1

    return f"Sent reminders to {count} users."

