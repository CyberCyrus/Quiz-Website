from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import text
from sqlalchemy import text

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tirth:tirth123@localhost/quiz_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

class UserScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Added date_taken


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    option_1 = db.Column(db.String(200), nullable=False)
    option_2 = db.Column(db.String(200), nullable=False)
    option_3 = db.Column(db.String(200), nullable=False)
    option_4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(200), nullable=False)

# Create admin account
def create_admin():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", password=generate_password_hash("admin123"), is_admin=True)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('admin_dashboard') if session['is_admin'] else url_for('quiz_dashboard'))
    return render_template('index.html')

# @app.route('/api/quizzes', methods=['GET'])
# def get_quizzes():
#     if 'user_id' not in session or not session['is_admin']:
#         return jsonify({'message': 'Unauthorized'}), 401

#     try:
#         quizzes = Quiz.query.all()
#         if not quizzes:
#             return jsonify([])  # Return an empty list if no quizzes exist

#         return jsonify([{ 'id': q.id, 'title': q.title } for q in quizzes])

#     except Exception as e:
#         print("Error loading quizzes:", str(e))
#         return jsonify({'message': 'Internal Server Error'}), 500
    
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required'}), 400

    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password, is_admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully', 'redirect': '/'})

@app.route('/api/admin/delete_quiz/<int:quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    if 'user_id' not in session or not session['is_admin']:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        quiz = Quiz.query.get(quiz_id)

        if not quiz:
            return jsonify({'message': 'Quiz not found'}), 404

        # ✅ First delete all associated questions
        db.session.query(Question).filter(Question.quiz_id == quiz_id).delete()

        # ✅ Then delete the quiz itself
        db.session.delete(quiz)
        db.session.commit()

        return jsonify({'message': 'Quiz deleted successfully'})

    except Exception as e:
        print("🔥 ERROR deleting quiz:", str(e))
        db.session.rollback()
        return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin

        # ✅ Fix: Return direct URLs instead of url_for()
        redirect_url = "/admin_dashboard" if user.is_admin else "/quiz_dashboard"
        return jsonify({'redirect': redirect_url})

    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))





@app.route('/quiz_dashboard')
def quiz_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('quiz_dashboard.html')

@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        quizzes = Quiz.query.all()
        return jsonify([{ 'id': q.id, 'title': q.title } for q in quizzes])

    except Exception as e:
        print("Error loading quizzes:", str(e))
        return jsonify({'message': 'Internal Server Error'}), 500



@app.route('/admin/manage_quiz')
def admin_manage_quiz():
    if 'user_id' not in session or not session['is_admin']:
        return redirect(url_for('home'))
    return render_template('manage_quiz.html')

@app.route('/api/admin/add_quiz', methods=['POST'])
def add_quiz():
    if 'user_id' not in session or not session['is_admin']:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        data = request.json
        if not data or 'title' not in data or not data['title'].strip():
            return jsonify({'message': 'Quiz title cannot be empty'}), 400

        new_quiz = Quiz(title=data['title'])
        db.session.add(new_quiz)
        db.session.commit()

        return jsonify({'redirect': url_for('add_questions', quiz_id=new_quiz.id)})

    except Exception as e:
        print("Error creating quiz:", str(e))
        db.session.rollback()
        return jsonify({'message': 'Internal Server Error'}), 500
    
    

@app.route('/admin/add_questions/<int:quiz_id>')
def add_questions(quiz_id):
    if 'user_id' not in session or not session['is_admin']:
        return redirect(url_for('home'))
    return render_template('add_questions.html', quiz_id=quiz_id)

@app.route('/api/admin/add_questions', methods=['POST'])
def add_questions_api():
    if 'user_id' not in session or not session['is_admin']:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.json
    if not data or 'questions' not in data or len(data['questions']) != 10:
        return jsonify({'message': 'You must add exactly 10 questions.'}), 400

    for q in data['questions']:
        new_question = Question(
            quiz_id=q['quiz_id'],
            question_text=q['question_text'],
            option_1=q['option_1'],
            option_2=q['option_2'],
            option_3=q['option_3'],
            option_4=q['option_4'],
            correct_option=q['correct_option']
        )
        db.session.add(new_question)

    db.session.commit()
    return jsonify({'message': 'All 10 questions added successfully'})

@app.route('/take_quiz/<int:quiz_id>')
def take_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('take_quiz.html', quiz_id=quiz_id)

@app.route('/api/questions/<int:quiz_id>', methods=['GET'])
def get_questions(quiz_id):
    try:
        questions = Question.query.filter_by(quiz_id=quiz_id).all()

        if not questions:
            return jsonify({'message': 'No questions found for this quiz'}), 404  # ✅ Proper error handling

        return jsonify([{ 
            "id": q.id,
            "question": q.question_text,
            "options": [q.option_1, q.option_2, q.option_3, q.option_4]
        } for q in questions])

    except Exception as e:
        print("🔥 ERROR in /api/questions:", str(e))  # Debugging print
        return jsonify({'message': 'Internal Server Error'}), 500



@app.route('/api/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        user_answers = data.get('answers', {})

        if not quiz_id or not isinstance(user_answers, dict):
            return jsonify({'message': 'Invalid quiz submission data'}), 400

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Quiz not found'}), 404

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        score = 0

        for question in questions:
            correct_answer = question.correct_option
            user_answer = user_answers.get(str(question.id), "")

            if user_answer == correct_answer:
                score += 1

        # ✅ Save score with `date_taken`
        new_score = UserScore(user_id=session['user_id'], quiz_id=quiz_id, score=score)
        db.session.add(new_score)
        db.session.commit()

        return jsonify({'success': True, 'score': score})

    except Exception as e:
        print("Error in /api/submit_quiz:", str(e))
        return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500





# @app.route('/api/user/scores', methods=['GET'])
# def get_user_scores():
#     if 'user_id' not in session:
#         return jsonify({'message': 'Unauthorized'}), 401

#     user_scores = (
#         db.session.query(UserScore, Quiz.title)
#         .join(Quiz, UserScore.quiz_id == Quiz.id)
#         .filter(UserScore.user_id == session['user_id'])
#         .order_by(UserScore.date_taken.desc())
#         .all()
#     )

#     score_data = []
#     for score, quiz_title in user_scores:
#         score_data.append({
#             "quiz_title": quiz_title,
#             "score": score.score,
#             "date_taken": score.date_taken.strftime("%Y-%m-%d %H:%M:%S")
#         })

#     return jsonify(score_data)

@app.route('/user_scores')  
def user_scores():
    if 'user_id' not in session:
        return redirect(url_for('home'))  # Redirect if not logged in
    return render_template('user_scores.html')  # ✅ This should return the HTML page


@app.route('/api/user_scores', methods=['GET'])
def get_user_scores():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        user_id = session['user_id']
        query = text("""
            SELECT quiz.title AS quiz_name, user_score.score, user_score.date_taken 
            FROM user_score 
            JOIN quiz ON user_score.quiz_id = quiz.id 
            WHERE user_score.user_id = :user_id 
            ORDER BY user_score.date_taken DESC
        """)

        scores = db.session.execute(query, {"user_id": user_id}).fetchall()

        if not scores:
            return jsonify([])  # Return an empty list if no scores exist

        formatted_scores = [
            {
                'quiz_name': score.quiz_name,
                'score': score.score,
                'date_taken': score.date_taken.strftime("%Y-%m-%d %H:%M") if score.date_taken else "N/A"
            }
            for score in scores
        ]

        print("✅ Retrieved scores:", formatted_scores)  # Debugging print
        return jsonify(formatted_scores)

    except Exception as e:
        print("🔥 ERROR in /api/user_scores:", str(e))  # Debugging print
        return jsonify({'message': 'Internal Server Error'}), 500
    
    
    
# @app.route('/admin/manage_quiz')
# def manage_quiz():
#     if 'user_id' not in session or not session['is_admin']:
#         return redirect(url_for('home'))
#     return render_template('manage_quiz.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session['is_admin']:
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html')

from sqlalchemy import text  # Ensure this import is at the top of your file

@app.route('/admin/view_scores')  
def admin_view_scores():
    if 'user_id' not in session or not session['is_admin']:
        return redirect(url_for('home'))
    return render_template('admin_view_scores.html')  # ✅ Ensure this file exists

@app.route('/api/admin/view_scores', methods=['GET'])
def get_all_user_scores():
    if 'user_id' not in session or not session['is_admin']:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        query = text("""
            SELECT user.username, quiz.title AS quiz_name, user_score.score, user_score.date_taken 
            FROM user_score 
            JOIN quiz ON user_score.quiz_id = quiz.id 
            JOIN user ON user_score.user_id = user.id 
            ORDER BY user_score.date_taken DESC
        """)

        scores = db.session.execute(query).fetchall()

        if not scores:
            return jsonify([])

        formatted_scores = [
            {
                'username': score.username,
                'quiz_name': score.quiz_name,
                'score': score.score,
                'date_taken': score.date_taken.strftime("%Y-%m-%d %H:%M") if score.date_taken else "N/A"
            }
            for score in scores
        ]

        return jsonify(formatted_scores)

    except Exception as e:
        print("🔥 ERROR in /api/admin/view_scores:", str(e))
        return jsonify({'message': 'Internal Server Error'}), 500

    
    
    




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
