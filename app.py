from flask import Flask, render_template, request, redirect, flash
from flask import jsonify 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from openai import OpenAI
from flask import session
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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", 
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///health.db"
app.config['SQLALCHEMY_DATABASE_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

class Register(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    Username = db.Column(db.String(500), nullable = False)
    Email = db.Column(db.String(100), unique = True, nullable = False)
    Contact = db.Column(db.String(15), nullable = False)
    Pass = db.Column(db.String(20), nullable = False)
    date = db.Column(db.DateTime, default=lambda : datetime.now(timezone.utc))
    wellness_records = db.relationship('wellness', backref='owner', lazy=True)
    def __repr__(self) -> str:
        return f"{self.sno} - {self.Username} - {self.Email} - {self.Pass} - {self.Contact}"

class wellness(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('register.sno'), nullable=False)
    Mood = db.Column(db.String(200), nullable = False)
    Describe = db.Column(db.String(200), nullable = False)
    Stress_Rate = db.Column(db.String(5), nullable = False)
    STRESS = db.Column(db.String(500), nullable = False)
    TYPE = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = lambda : datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f"{self.sno} - {self.Mood} - {self.Stress_Rate} - {self.TYPE}"

class log(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    User = db.Column(db.String(500), nullable = False)
    Pass = db.Column(db.String(100), nullable = False)
    def __repr__(self) -> str:
        return f"{self.sno} - {self.User} - {self.Pass}"

class schedule(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    NAME = db.Column(db.String(500), nullable = False)
    DATE = db.Column(db.String(100), nullable = False)  
    EMAIL = db.Column(db.String(100), nullable = False)
    DESCRIPTION = db.Column(db.String(500), nullable = False)
    def __repr__(self) -> str:
        return f"{self.sno} - {self.NAME} - {self.DATE}"



QUESTIONS = [
    {"id": 0, "q": "Overwhelmed: How often have you felt that you were unable to control the important things in your life?", "options": ["Never", "Sometimes", "Often", "Always"]},
    {"id": 1, "q": "Restlessness: How often have you felt so restless that it was hard to sit still?", "options": ["Never", "Sometimes", "Often", "Always"]},
    {"id": 2, "q": "Anhedonia: How often have you had little interest or pleasure in doing things you normally enjoy?", "options": ["Never", "Sometimes", "Often", "Always"]},
    {"id": 3, "q": "Sleep Quality: How often have you had trouble falling or staying asleep, or felt like you were sleeping too much?", "options": ["Never", "Sometimes", "Often", "Always"]},
    {"id": 4, "q": "Focus: How often have you found it difficult to concentrate on tasks, such as reading or working?", "options": ["Never", "Sometimes", "Often", "Always"]},
    {"id": 5, "q": "Self-Perception: How often have you felt bad about yourself—or that you are a failure or have let yourself or your family down?", "options": ["Never", "Sometimes", "Often", "Always"]},
    {"id": 6, "q": "Social Withdrawal: How often have you felt the urge to avoid social interactions or felt lonely even when around others?", "options": ["Never", "Sometimes", "Often", "Always"]},
    {"id": 7, "q": "Physical Tension: How often have you experienced physical symptoms of stress, such as headaches, muscle tension, or an upset stomach?", "options": ["Never", "Sometimes", "Often", "Always"]},
    {"id": 8, "q": "Irritability: How often have you felt easily annoyed, irritable, or on edge?", "options": ["Never", "Sometimes", "Often", "Always"]},
    {"id": 9, "q": "Future Outlook: How often have you felt pessimistic or hopeless about your future?", "options": ["Never", "Sometimes", "Often", "Always"]},    
]

BOT_RESPONSES = {
    "hello": "Hi there! I'm your Mindset Assistant. How are you feeling?",
    "stress": "It sounds like you're feeling stressed. Have you tried our breathing exercises?",
    "sad": "I'm sorry to hear that. Remember, it's okay to feel this way. Would you like to talk to an expert?",
    "help": "I can help you navigate the portal, suggest exercises, or just listen!",
    "quiz": "You can take our mental health assessment at the /quiz page to track your stress levels.",
    "default": "I'm still learning! Try asking about 'stress', 'quiz', or just say 'hello'."
}

@app.route('/quiz', methods=['GET', 'POST'])
def assessment():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        answers = request.form.get('all_answers').split(',')
        total_score = sum([int(a) for a in answers])
        
        status = "Low Stress"
        if total_score > 20: status = "Severe Stress"
        elif total_score > 15: status = "High Stress"
        elif total_score > 10: status = "Moderate Stress"
        elif total_score > 5 : status = "Regular"

        new_entry = wellness(
            user_id=session['user_id'],
            Mood="Assessed", 
            Describe="Quiz Completion", 
            Stress_Rate=str(total_score), 
            STRESS=status,
            TYPE = "QUIZ"
        )
        db.session.add(new_entry)
        db.session.commit()
        
        return render_template('results.html', score=total_score, status=status)

    return render_template('quiz.html', questions=QUESTIONS)


@app.route('/', methods = ['GET','POST'])
def front():
    if(request.method == 'POST'):
        User = request.form['username']
        email = request.form['email']
        cont = request.form['contact']
        passw = request.form['password']

        existing_user = Register.query.filter_by(Email=email).first()

        if existing_user:
            flash("User with this email already exists. Please login instead.", "danger")
            return redirect('/')

        try:
            HealthRegister = Register(Username=User, Email=email, Contact=cont, Pass=passw)
            db.session.add(HealthRegister)
            db.session.commit()
            
            session['user_id'] = HealthRegister.sno 
            session['username'] = HealthRegister.Username
            return redirect('/home')
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            return redirect('/')
            
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
        
    user_history = wellness.query.filter_by(user_id=session['user_id']).all()
    user_info = Register.query.get(session['user_id'])
    
    return render_template('dashboard.html', history=user_history, user=user_info)


@app.route('/excercises')
def exc():
    return render_template('exercises.html')
    

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        USER = request.form['user']
        pasw = request.form['pass']
        
        user_record = Register.query.filter_by(Username=USER, Pass=pasw).first()
        
        if user_record:
            session['user_id'] = user_record.sno
            session['username'] = user_record.Username
            return redirect('/home')
        else:
            return "Invalid Credentials"
    return render_template('1.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/schedule')
def shed():
    return render_template('3.1.html')


@app.route('/library')
def lib():
    return render_template('2.html')


@app.route('/appointment')
def appo():
    return render_template('3.html')


@app.route('/emergency')
def emer():
    return render_template('4.html')


@app.route('/mindfullness')
def mind():
    return render_template('mindfullness.html')


@app.route('/meditation')
def med():
    return render_template('meditation.html')


@app.route('/breathing')
def breath():
    return render_template('breathing.html')


@app.route('/cognitive')
def cog():
    return render_template('cognitive.html')


@app.route('/connect')
def con():
    return render_template('connect.html')


@app.route('/gratitude')
def grat():
    return render_template('gratitude.html')


@app.route('/physical')
def pyh():
    return render_template('physical.html')


@app.route('/sleep')
def slep():
    return render_template('sleep.html')


@app.route('/history')
def hist():
    if 'user_id' not in session:
        return redirect('/login')
    
    alldata = wellness.query.filter_by(user_id=session['user_id']).all()
    return render_template('history.html', alldata=alldata)

@app.route('/therapists', methods = ['GET'])
def therapists():
    return render_template('therapist.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_data = request.get_json()
    user_text = user_data.get("message", "")

    system_instruction = (
        "You are the 'Mindset AI' assistant. Your goal is to be a supportive, empathetic guide. "
        "1. Keep initial greetings short and warm. "
        "2. Only suggest the Assessment Quiz (/quiz) or Exercises (/excercises) if the user expresses "
        "uncertainty about their health or asks for help. "
        "3. If they mention feeling overwhelmed or in danger, immediately provide the link to /emergency. "
        "4. Use a conversational tone; do not list all your capabilities in one go."
    )

    try:
        response = client.chat.completions.create(
            
            model="google/gemini-2.0-flash-001", 
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ],
            extra_headers={
                "HTTP-Referer": "http://localhost:5000", 
                "X-Title": "Mindset Architecture App",
            }
        )
        
        bot_answer = response.choices[0].message.content
        
        return jsonify({"response": bot_answer})

    except Exception as e:
        print(f"OpenRouter Error: {e}")
        return jsonify({"response": "I'm having a connection issue. Please try again."})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug = True)
