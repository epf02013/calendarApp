import datetime
import calendar
import time
import json
from couchbase.bucket import Bucket
from couchbase.exceptions import KeyExistsError, NotFoundError
from couchbase.views.params import Query

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

@app.route("/signup")
def signup():
		return render_template("signup.html")



@app.route("/")
def index() :
	user_id = session.get("user_id")
	if not user_id :
		return render_template("index.html")
	else :
		user = db.User.get_from_id(user_id)

		cal  = calendar.Calendar()
		
		year = time.localtime()[0]
		month = time.localtime()[1]

		days = [cal.monthdatescalendar(year, month + 1)]

		return render_template("calendar.html", days = days)

dbName= 'couchbase://localhost/calendarDb'

def connect_db():
    return Bucket(CONNSTR)

db = connect_db()

if __name__ == "__main__" : 
	app.run(debug=True)
	
	
