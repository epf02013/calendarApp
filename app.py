import datetime
import calendar
import time
from flask import Flask, render_template, request, session, redirect, url_for


app = Flask(__name__)


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
	
	
