from flask import Flask, render_template,redirect,session,abort,request,url_for,g,flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 

app=Flask(__name__)
bcrypt=Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False 
db= SQLAlchemy(app)

@app.before_request
def before_request():
    
    users=User.query.all()
    g.user=None
    if 'user_id' in session:
        user = [x for x in users if x.id==session['user_id']][0]
        g.user = user

class User(db.Model):
    id =db.Column('id',db.Integer,primary_key=True)
    name=db.Column('name',db.String(50),unique=True) 
    email=db.Column('email',db.String(50))
    phone=db.Column('phone',db.String(50))
    password=db.Column('password',db.String(50))
    score=db.Column('score',db.Integer)
    nextq=db.Column('next',db.Integer)

    def __init__(self,name,email,phone,password,score,nextq):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password
        self.score=score
        self.nextq=nextq


class Quiz(db.Model):
    id=db.Column('id',db.Integer,primary_key=True)
    q=db.Column('questions',db.String(1000)) 
    a=db.Column('answer',db.String(200))
    o=db.Column('options',db.String(400))

    def __init__(self,q,o,a):
        self.q=q 
        self.a=a
        self.o=o 


def user_already_exists(users, email):
    for user in users:
        if user.email == email:
            return True
    return False


@app.route('/',methods=['GET','POST'])
def home():
    if not g.user:
        return render_template('home.html')
    else:
        return render_template('profile.html')

    return render_template('home.html')



@app.route('/register',methods=['GET','POST'])
def register():
    
    error=''
    status = ''
    users = User.query.all()

    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        phone=request.form['phone']
        password=request.form['password']
        confirmpassword=request.form['confirmpassword']

        if user_already_exists(users, email):
            status = 'show'
            error = 'User already exists'
        else:
            if password==confirmpassword: 
                score=0
                nextq=0
                pw_hash=bcrypt.generate_password_hash(password)
                new_user=User(name,email,phone,pw_hash,score,nextq)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                status = 'show'
                error="Password didn't match"
                return render_template('register.html', status=status, error=error)

    return render_template('register.html', status=status, error=error)

    
@app.route('/login',methods=['GET','POST'])
def login():

    users=[]
    error=''
    status = ''
    users= User.query.all()
    if request.method=='POST':
        session.pop('user_id',None)
        email=request.form['email']
        password=request.form['password']
        user=None
        #user= [x for x in users if x.email==email ][0]
        for x in users:
            if x.email == email:
                user = x
                break

        if user and bcrypt.check_password_hash(user.password,password):
            session['user_id']=user.id
            session["log"]=True
            flash('You were successfully logged in', "message")
            return redirect(url_for('profile'))
        elif user == None:
            status = 'show'
            error="Incorrect credentials or user does not exist. Please Register"
        else:
            status = 'show'
            error = 'Incorrect email address or password'
        
        return render_template('login.html', status=status, error=error)
    return render_template('login.html', status=status, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile',methods=['GET','POST'])
def profile():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('profile.html')


@app.route('/quiz',methods=['GET','POST'])
def quiz():
    done=False
    u=User.query.filter_by(name=g.user.name).first()
    total_questions=5
    question_num=u.nextq

    if int(question_num)>total_questions:
        u.nextq=total_questions
        current_question=Quiz.query.filter_by(id=total_questions).first()
        done=True

    elif question_num==0:
        ques=Quiz.query.filter_by(id=1).first()
        current_question=ques

    elif (question_num!=0) and question_num<=total_questions:
        ques=Quiz.query.filter_by(id=question_num).first()
        current_question=ques 
    
    score=int(u.score)
    opt=str(current_question.o)
    opt=opt.split(',')

    return render_template('quiz.html',current_question=current_question,score=score,opt=opt,done=done)

@app.route('/process/<current_question>',methods=['POST'])
def process(current_question):
    
    question_num=int(current_question)
    ques=Quiz.query.filter_by(id=question_num).first()
    u=User.query.filter_by(name=g.user.name).first()
    score=int(u.score)

    answer=request.form['ans']

    if str(answer)==str(ques.a):
        score+=int(1)
        
    
    else:
         flash('Previous answer was Wrong. Answer carefully')

    question_num+=int(1)
    u.score=score
    u.nextq=question_num 
    db.session.commit()

    return redirect(url_for('quiz'))


@app.route('/about')
def about():
    return render_template('about.html')

if __name__=='__main__':
    # app.debug=True
    app.secret_key="efrwwseq4sfcwasdr3142qwdsf24wsd"
    app.run() 