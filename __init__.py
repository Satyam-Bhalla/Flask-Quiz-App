# Importing Files
from flask import Flask, render_template, request, redirect, session, url_for,Markup
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, BooleanField, SubmitField,RadioField
from pymongo import MongoClient
from wtforms.validators import InputRequired, Length
import random
import requests
import base64
from plotly.offline import plot
from plotly.graph_objs import Scatter



# Initializing global variables
app = Flask(__name__)
app.config['SECRET_KEY']= 'confidential'
client = MongoClient("mongodb://user:user123@ds145146.mlab.com:45146/quiz-app")
db = client['quiz-app']
users = db.users


a,b,c,d = '','','',''
correct_ans = []
given_ans = []


# For making different user objects
class SignupForm(FlaskForm):
	username = TextField('username',validators=[InputRequired()])
	password = PasswordField('password',validators=[InputRequired(), Length(min=3, max=16)])
	choice = RadioField('Answer', choices=[(a,'A'),(b,'B'),(c,'C'),(d,'D')])

@app.route('/', methods=['POST','GET'])
def index():
	form = SignupForm()
	msg = ''
	if request.method == 'POST':
		search = users.find_one({'username':form.username.data})
		if search:
			msg = 'Username already exists'
		else:
			users.insert({'username':form.username.data,'password':form.password.data})
			return redirect(url_for('login'))

	return render_template('signup.html', form=form, msg=msg)

@app.route('/login', methods=['POST','GET'])
def login():
	form = SignupForm()
	msg = 'Invalid Username or Password'
	if request.method == 'POST':
		search = users.find_one({'username':form.username.data})
		if search:
			authu = search['username']
			authp = search['password']
			if authu == form.username.data and authp == form.password.data:
				session['username'] = form.username.data
				return redirect(url_for('trivia', name=authu))
		
		return render_template('index.html', msg=msg, form=form)

	return render_template('index.html', form=form)

@app.route('/trivia')
@app.route('/trivia/<name>')
def trivia(name):
	r = requests.get('https://opentdb.com/api_category.php')
	json_object = r.json()
	category = []
	category_id = []
	for i in range(23):
		category.append(json_object["trivia_categories"][i]["name"])
		category_id.append(json_object["trivia_categories"][i]["id"])
	return render_template('categories.html',category=category,category_id=category_id)

@app.route('/question/<id_name>' ,methods=['POST','GET'])
def question(id_name):
	form = SignupForm()
	r = requests.get('https://opentdb.com/api.php?amount=10&category='+id_name+'&difficulty=easy&type=multiple&encode=base64')
	json_object = r.json()
	quest = []
	correct_ans.clear()
	given_ans.clear()
	incorrct_ans = []
	for i in range(10):
		quest.append(base64.b64decode(json_object['results'][i]['question']).decode('UTF-8'))
		correct_ans.append(base64.b64decode(json_object['results'][i]['correct_answer']).decode('UTF-8'))
		incorrct_ans.append(json_object['results'][i]['incorrect_answers'])
	options = []
	for i in range(10):
		options.append([correct_ans[i]])
		for j in range(3):
			options[i].append(base64.b64decode(incorrct_ans[i][j]).decode('UTF-8'))


	for i in range(10):
		random.shuffle(options[i])

	return render_template('questions.html',quest=quest,correct_ans=correct_ans,options=options, form=form)


@app.route('/result',methods=['POST'])
def result():

	count = 0
	new = []
	for i in range(10):
		given_ans.append(request.form[str(i)]) 
		if request.form[str(i)]==correct_ans[i]:
			count+=1
			new.append(1)
		else:
			new.append(0)
	msg = ''
	if count<3:
		msg="Poor Result...Shame on You"
	elif count>8:
		msg="Excellent Result...Your Parents Must Be Proud"
	else:
		msg = "NICE ONE"
	p = plot([Scatter(x=[1,2,3,4,5,6,7,8,9,10], y=new )],output_type="div")
	return render_template('result.html',count=count,given_ans=given_ans,correct_ans=correct_ans,msg=msg,div_placeholder=Markup(p))


@app.route('/logout')
def logout():
	session['username'] = None
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.secret_key= 'confidential'
	app.run(debug=True)
