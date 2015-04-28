import datetime
import calendar
import time
import json
from couchbase.bucket import Bucket
from couchbase.exceptions import KeyExistsError, NotFoundError
from couchbase.views.params import Query
import fb_grabber.py
from flask import Flask, render_template, request, session, redirect, url_for


class user(object):
	def _init_(self, firstName, lastName, email, age, doc=None):
		self.firstName=firstName
		self.lastName=lastName
		self.email=email
		self.age=age
		if doc and doc.success:
			doc=doc.value
		else:
			doc=None
		self.doc=doc
		
app = Flask(__name__)
dbName= 'couchbase://localhost/calendarDb'

def connect_db():
    	return Bucket(dbName)
db=connect_db()


@app.route("/login", methods=['GET', 'POST'])
def login():
	return render_template("login.html")


@app.route("/logout", methods=['GET', 'POST'])
def logout():
        session['logged_in']=False
	return render_template("logout.html")


#@app.route("/registerUser")
#def registerUser(form):
#	doc={}
#	for k, v in form.items():
#		doc[k]=v
#	if not 'firstName' in doc or not doc['firstName']:
#		return None, ("Must have First Name", 400)
#	if not 'lastName' in doc or not doc['lastName']:
#		return None, ("Must have Last Name", 400)
#	if not 'email' in doc or not doc['email']:
#		return None, ("Must have email", 400)
#	if not 'age' in doc or not doc['age']:
#		return None, ("Must have age", 400)
	
#	try:
#		db.add(doc['email'],doc)
#		return redirect("/registered")
#	except KeyExistsError:
#		return "Sorry that email is already in use", 400


#extra slashes may be because everything is stored in docs as json text and then doc is dumped
@app.route("/logged_in", methods=['GET', 'POST'])
def logged_in():
        session['logged_in']=True
        temp=""+request.form['user_info']
        user_info=json.loads(temp)
        del user_info['gender']
        del user_info['locale']
        del user_info['timezone']
        del user_info['verified']
        user_info['access_token']=request.form['access_token']
        user_id=user_info['id']
        try :
                db.add(user_id, json.dumps(user_info))
                user_info['events']=get_fb_events(user_id, user_info['access_token'])
                db.set(user_id, json.dumps(user_info))

        except KeyExistsError:
                doc=db.get(user_id)
                doc=doc.value
                doc=json.loads(doc)
                del doc['access_token']
                doc['access_token']=user_info['access_token']
                doc['events']=updateEvents(user_id,doc['access_token'], doc['events'])
                db.set(user_id, json.dumps(doc))

        return render_template("logged_in.html", logged_in="trueuu")
@app.route("/")
def index() :
	user_id = session.get("user_id")
	
	#if not user_id :
	#	return render_template("login.html")
	#else:
	#	user = db.User.get_from_id(user_id)

	cal  = calendar.Calendar()
	
	year = time.localtime()[0]
	month = time.localtime()[1]

	days = cal.monthdatescalendar(year, month + 1)

	print days
        try:
                if (session['logged_in']) :
                        return render_template("calendar.html", days = days)
                else:
                        return render_template("login.html")
        except KeyError:
                        return render_template("login.html")

if __name__ == "__main__" : 
        app.secret_key="secretive_key"
	app.run(debug=True)
	sess.init_app(app)
	
