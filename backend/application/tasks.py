from celery import shared_task
from .models import User,Subject,Chapter,Quiz,Scores
from .utils import fromat_report
import time
import csv
import io
from collections import Counter


@shared_task(ignore_results=False,name = "csv_report")
def csv_report():
    
    csv_filename="UserQuizDetails.csv"
    with open(f'./Source/csv_files/{csv_filename}','w',newline="") as csvfile:
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

@shared_task(ignore_results=False,name = "montly_report")
def montly_report():

    return "Monthly report sent"

@shared_task(ignore_results=False,name = "daily_reminder")
def daily_reminder():
    return "daily reminder for user"

