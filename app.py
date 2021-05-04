from flask import Flask, render_template, request,session,redirect,url_for
import MySQLdb
from database import Database as Mydatabase
from MySQLdb.cursors import DictCursor
from random import randrange
import random as rand
import time
import datetime
from flask_mail import Mail, Message
import smtplib, ssl



app = Flask(__name__,static_folder='static',
            template_folder='templates')

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'vempadasivakumarreddy@gmail.com',
    MAIL_PASSWORD = 'Siva@2501'
)
mail= Mail(app)



def sendotponmail(Email, xx,Name):
    var1 = ('Hi %s, <br>Your One time password is : <b>%s</b><br><br>Thanking you,<br>Evoluzn Inc<p align = "justify"><br><br><b>This is a system generated email. You are requested not to reply on this.</b><br><br><b>Disclaimer :</b> This e-mail message is for the sole use of the intended recipient(s) and may contain certain confidential and privileged information. Any unauthorized review, use, disclosure or distribution is prohibited. If you are not the intended recipient, please contact the sender by e-mail and destroy all copies of the original message.</p>'%(Name, xx))
    fromaddr = app.config.get('MAIL_USERNAME')
    toaddrs = Email
    print(fromaddr)
    print(toaddrs)
    print(xx)
    var22 = Message("One time password for Registering in intelliZENS", sender=fromaddr, recipients=[toaddrs])
    var22.html = var1
    mail.send(var22)
    print(Email)
    return True

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        xx = str(rand.randrange(100000, 999999))
        Name = request.form.get('name')
        Email = request.form.get('email')
        Mobile = request.form.get('mobile')
        Qualification = request.form.get('qualification')
        Course = request.form.get('course')
        Year_of_Passout = request.form.get('passout')
        Password = request.form.get('password')
        
        session['email'] = request.form.get('email')
        if 'email' in session:
            e = session['email']
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()

        if Email and Mobile:
            cursor.execute("select * from quiz where Mobile = %s or Email = %s",[Mobile,Email])
        elif Email:
            cursor.execute("select * from quiz where Email = %s",[Email])
        else:
            cursor.execute('select * from quiz where Mobile = %s', [Mobile])
        msg = cursor.fetchone()
        if not msg:
            sql = "INSERT INTO quiz (UserRegDate, Name,Email, Mobile, Qualification, Course, Year_of_Passout, Password,OTP) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)"
            cursor.execute(sql, (time.strftime('%Y-%m-%d %H:%M:%S'), Name, Email, Mobile, Qualification, Course, Year_of_Passout, Password, xx,))
            if cursor.rowcount > 0:
                retval = sendotponmail(Email, xx, Name)
                if retval == True:
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return render_template('verify.html', email = e)
                else:
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    return "<h1>User registraion Failed </h1>"
            else:
                conn.rollback()
                cursor.close()
                conn.close()
                return "<h1>User registration Failed </h1>"
        else:
            conn.rollback()
            cursor.close()
            conn.close()
            if msg['Email'] == Email:
                return "<h1>Email Already registered! </h1>"
        cursor.close()
    return render_template ('index.html')

@app.route('/otp_confirmation/', methods=['GET', 'POST'])
def otp_confirmation():
    if request.method == 'POST':
        Email = request.form.get('email')
        OTP = request.form.get('OTP')
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()
        if Email:
            Email = Email
        cursor.execute('select * from quiz where Email = %s',[Email])
        msg = cursor.fetchone()
        if msg:
            if msg['OTP'] == OTP:
                
                cursor.execute('update quiz set OTPVerifed = 1 where Email =%s', [Email])
                conn.commit()
                cursor.close()
                conn.close()
                return render_template('confirm.html')
            else:
                conn.rollback()
                conn.commit()
                conn.close()
                return "<h1>Incorrect OTP</h>"
    else:
        return "<h1>Email not found!</h1>"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method ==  'POST':
        Email = request.form.get('email')
        Password = request.form.get('password')
        session['email'] = request.form.get('email')
        if 'email' in session:
            e = session['email']
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()

        if Email:
            Email = Email
        cursor.execute('select * from quiz where(Email = %s)', [Email])
        msg = cursor.fetchone()
        if msg:
            if msg['Password'] == Password:
                conn.commit()
                cursor.close()
                conn.close()
                return render_template('quiz.html', questions_list = questions_list, email =e)
            else:
                conn.commit()
                cursor.close()
                conn.close()
                return "<h1>Incorrect Password!</h1>"
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return "<h1>Email/Mobile not registered!</h1>"
        cursor.close()
    else:
        return render_template('login.html')

@app.route('/send_email_otp', methods=['GET', 'POST'])
def send_email_otp() :
    if request.method == 'POST':
        xx = str(rand.randrange(100000, 999999))
        Name = request.form.get('name')
        Email = request.form.get('email')
        if 'email' in session:
            e = session['email']
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()
        
        cursor.execute("select * from new_table where Email = %s", [Email])
        msg = cursor.fetchone()
        if msg:
            cursor.execute("update new_table set OTP = %s, OTPVerified = 0 where Email = %s", (xx, Email))
            retval = sendotponmail(Email,xx, msg['Name'])
            if retval == True:
                conn.commit()
                cursor.close()
                conn.close()
                return render_template('verify.html', email = e)
            else:
                conn.rollback()
                cursor.close()
                conn.close()
                return "<h1>Request to resend OTP</h1>"
        else:
            conn.rollback()
            cursor.close()
            conn.close()
            return "<h1>Email Id not registered!</h1>"
    else:
        return render_template('Resend_email_otp.html' )

class Question:
    q_id = -1
    question = ""
    option1= ""
    option2=""
    option3=""
    option4=""
    correctOption = -1
    not_selected_option = ""
    
    

    def __init__(self, q_id, question, option1, option2, option3, option4, correctOption,not_selected_option ):
        self.q_id = q_id
        self.question = question
        self.option1 = option1
        self.option2 = option2
        self.option3 = option3 
        self.option4 = option4
        self.correctOption = correctOption
        self.not_selected_option = not_selected_option

    def get_correct_option(self):
        if self.correctOption == 1:
            return self.option1
        elif self.correctOption == 2:
            return self.option2
        elif self.correctOption == 3:
            return self.option3
        elif self.correctOption == 4:
            return self.option4
        else:
            return 0
        
    def get_not_selected_option(self):
        if self.not_selected_option is None:
            return ''
   


q1 = Question(1, "What id Capital of Andhra Pradesh?", "Vizag", "Amaravathi", "Karnool", "Tirupathi",1,'')
q2 = Question(2, "Largest River in India?", "Godavari", "Yamuna", "cavari", "Ganaga", 4,'')
q3 = Question(3, "In Which season rains will be more?", "Summer", 'Winter', "Rainy", "Spring",3,'')


questions_list = [q1, q2, q3]

@app.route("/quiz")
def quiz():
    session['email'] = request.form.get('email')
       
    if 'email' in session:
            e = session['email']

    return render_template('quiz.html', questions_list = questions_list, email = e)

@app.route('/Quiz1', methods=['GET', 'POST'])
def Quiz():
    question = []
    if 'email' in session:
        e = session['email']
    if request.method == 'POST':
        Email = e
        question1 = request.form.get('question1')
        session['email'] = request.form.get('email')
        print(Email)
        
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()
        print('ok')
        if Email:
            Email = Email
        cursor.execute('select * from quiz where Email =%s', ['Email'])
        msg = cursor.fetchone()
        if msg:
            cursor.execute('select * from questions where question1 = %s and idquiz = %s',( (question1),msg['idquiz']))
            found = cursor.fetchone()
            if not found:
                for result in found:
                    question.append(result['question1'])
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return question
                

    return render_template('quiz1.html', q=question,email = e)

@app.route("/submitquiz", methods=['GET', 'POST'])
def submitquiz():
    correct_count = 0
    selected_option=[]
    correct_option=[]
    Question=[]
    if 'email' in session:
        e=session['email']
    if request.method == 'POST':
        Email = e
        SrNo = request.form.get('SrNo')
        Question1 = request.form.get('q1')
        Question2 = request.form.get('q2')
        Question3 = request.form.get('q3')
        option = request.form.get('option')
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()
        if Email:
            cursor.execute('select * from quiz where Email = %s', [Email])
        print(Email)
        msg = cursor.fetchone()
        if msg:
            cursor.execute('select * from score where SrNo = %s and idquiz = %s',( msg['idquiz'],[SrNo]))
            found = cursor.fetchone()
            if not found:
                for question in questions_list:
                    qid = str(question.q_id)
                    q=str(question.question)
                    Question.append(q)
                    selected_options = request.form[qid]
                    not_selected_options = str(question.not_selected_option)
                    selected_option.append(selected_options)
                    correct_options = question.get_correct_option()
                    correct_option.append(correct_options)
                    print(not_selected_options)
                    
                    

                    if selected_options == correct_options:
                        correct_count = correct_count + 1
                    elif selected_options == None:
                        correct_count = correct_count + 0
                else:
                    correct_count = correct_count + 0
                    

                if str(question.question) == 'None':
                    correct_count = correct_count +0

                    
                total_count = str(correct_count )
                        
                Question1 = Question[0]
                Question2 = Question[1]
                Question3 = Question[2]
            
                correct_option1 =correct_option[0]
                correct_option2 = correct_option[1]
                correct_option3 = correct_option[2]
                selected_option1 = selected_option[0]
                selected_option2 = selected_option[1]
                selected_option3 = selected_option[2]
                
                
                sql = "INSERT INTO score (total_count, idquiz,Question1,correct_option1,selected_option1,Question2, correct_option2, selected_option2, Question3,correct_option3 , selected_option3) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (total_count,msg['idquiz'],Question1,correct_option1, selected_option1,  Question2,correct_option2, selected_option2,  Question3,correct_option3 , selected_option3))
                conn.commit()
                cursor.close()
                conn.close()


    return render_template('score.html', c=total_count, email =e)


if __name__ == "__main__":
    app.run(debug=True)


