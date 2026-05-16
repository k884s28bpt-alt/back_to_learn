from flask import Flask, render_template, request, redirect, session
from database import init_db
from logic import (login_user, register_user, get_user_topics,
                   add_topic, update_topic_status, delete_topic)

app = Flask(__name__)
app.secret_key = 'back_to_learn_secret_2026'

with app.app_context():
    init_db()

def is_logged_in():
    return 'user_id' in session

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect('/dashboard')
    if request.method == 'POST':
        username   = request.form.get('username', '')
        password   = request.form.get('password', '')
        last_grade = request.form.get('last_grade', '')
        success, message = register_user(username, password, last_grade)
        if success:
            return redirect('/login')
        else:
            return render_template('register.html', error=message)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect('/dashboard')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = login_user(username, password)
        if user:
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['grade']    = user['last_grade']
            return redirect('/dashboard')
        else:
            return render_template('login.html',
                                   error="Wrong username or password")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect('/login')
    topics = get_user_topics(session['user_id'])
    return render_template('dashboard.html',
        username = session['username'],
        grade    = session['grade'],
        topics   = topics
    )

@app.route('/add', methods=['POST'])
def add():
    if not is_logged_in():
        return redirect('/login')
    add_topic(
        session['user_id'],
        request.form.get('subject', ''),
        request.form.get('topic_name', ''),
        request.form.get('grade_level', '')
    )
    return redirect('/dashboard')

@app.route('/update/<int:topic_id>', methods=['POST'])
def update(topic_id):
    if not is_logged_in():
        return redirect('/login')
    update_topic_status(
        topic_id,
        session['user_id'],
        request.form.get('status', 'not_started')
    )
    return redirect('/dashboard')

@app.route('/delete/<int:topic_id>', methods=['POST'])
def delete(topic_id):
    if not is_logged_in():
        return redirect('/login')
    delete_topic(topic_id, session['user_id'])
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)