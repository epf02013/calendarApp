import datetime, calendar, json, time               # utility libraries
from couchbase.bucket import Bucket                 # we need this to link up to the DB 
from couchbase.exceptions import KeyExistsError, NotFoundError
from couchbase.views.params import Query
from fb_grabber import get_fb_events, updateEvents, format_event       
from flask import Flask, render_template, request, session, redirect, url_for
from models import user, dbName                           # M in MVC


bDays={}

app = Flask(__name__)

# connect to Couchbase 
def connect_db():
    return Bucket(dbName)
db=connect_db()


@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    # Change the session variable which is responsive on all pages
    session['logged_in']=False
    return render_template("logout.html")


@app.route("/addEvent", methods=['GET', 'POST'])
def addEvent():
    # add a new event given a date, time, event name

    # use the calendar library for calendar manipulation
    cal  = calendar.Calendar()
    year = time.localtime()[0]
    month = time.localtime()[1]
    days = cal.monthdatescalendar(year, month)    

    # call db to get user events
    doc = db.get(session['user_id'])
    doc = doc.value
    doc = json.loads(doc)
    pop = json.loads(doc['events'])
    temp = pop['data']
    
    # add the new event to the DB
    new_event = {}
    new_event["name"] = request.form["name"]
    new_event["id"] = request.form["name"]+request.form['start_time'] 
    new_event['start_time'] = request.form['start_time']
    new_event['end_time'] = request.form['end_time']
    temp.append(format_event(new_event))
    pop['data']=temp
    doc['events']=json.dumps(pop)
    # store the JSON blob into DB with primary key: user_id
    db.set(session['user_id'], json.dumps(doc))
    
    global bDays
    temp=bDays
    temp[int(new_event['start_time'][8:10])]=("plop", int(request.form['start_time'][5:7]))
    bdays=temp
    return render_template("calendar.html", days=days, bDays=bDays)


@app.route("/logged_in", methods=['GET', 'POST'])
def logged_in():
    # calendar manipulation
    cal  = calendar.Calendar()
    year = time.localtime()[0]
    month = time.localtime()[1]
    days = cal.monthdatescalendar(year, month)

    # logged_in session variable is now T
    session['logged_in']=True
    temp=str(request.form['user_info'])
    user_info=json.loads(temp)
    
    # we don't really care about some of the stuff facebook returns, so we delete it 
    # so it doesn't get waste space in the database 
    del user_info['gender']
    del user_info['locale']
    del user_info['timezone']
    del user_info['verified']
    
    user_info['access_token'] = request.form['access_token']
    user_id=user_info['id']
    # try getting the users facebook events, could result in some exception
    try :
        # set the session variable, an add the user to the database
        session['user_id'] = user_id
        db.add(user_id, json.dumps(user_info))
        # try to get facebook events 
        user_info['events'] = get_fb_events(request.form['user_events'])
        temp = json.loads(user_info['events'])
        db.set(user_id, json.dumps(user_info))
    except KeyExistsError:
        doc = db.get(user_id)
        doc = doc.value
        doc = json.loads(doc)
        del doc['access_token']
        doc['access_token'] = user_info['access_token']
        doc['events'] = updateEvents(request.form['user_events'], doc['events'])
        temp = json.loads(doc['events'])
        db.set(user_id, json.dumps(doc))
    
    eventsDays={}
    for event in temp['data'] :
        eventsDays[int(event['start_time'][8:10])]=("https://www.facebook.com/events/"+event['id'], int(event['start_time'][5:7]))
    global bDays
    bDays=eventsDays
    return render_template("calendar.html", days=days, bDays=bDays)


@app.route("/")
def index() :
    user_id = session.get("user_id")
    
    # calendar stuff
    cal  = calendar.Calendar()
    year = time.localtime()[0]
    month = time.localtime()[1]
    days = cal.monthdatescalendar(year, month )
    global bDays

    try:
        if (session['logged_in']) :
            return render_template("calendar.html", days =days, bDays=bDays)
        else:
            return render_template("login.html")
    except KeyError:
        return render_template("login.html")


# this is where we run the app!
if __name__ == "__main__" : 
    app.secret_key="secretive_key"
    app.run(debug=True)
    sess.init_app(app)
