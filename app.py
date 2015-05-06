import datetime 
import calendar
import time
import json
from couchbase.bucket import Bucket
from couchbase.exceptions import KeyExistsError, NotFoundError
from couchbase.views.params import Query
from fb_grabber import get_fb_events, updateEvents, format_event
from flask import Flask, render_template, request, session, redirect, url_for

bDays={}

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
#   doc={}
#   for k, v in form.items():
#       doc[k]=v
#   if not 'firstName' in doc or not doc['firstName']:
#       return None, ("Must have First Name", 400)
#   if not 'lastName' in doc or not doc['lastName']:
#       return None, ("Must have Last Name", 400)
#   if not 'email' in doc or not doc['email']:
#       return None, ("Must have email", 400)
#   if not 'age' in doc or not doc['age']:
#       return None, ("Must have age", 400)

#   try:
#       db.add(doc['email'],doc)
#       return redirect("/registered")
#   except KeyExistsError:
#       return "Sorry that email is already in use", 400

@app.route("/manageEvents")
def manageEvents():
    doc=db.get(session['user_id'])
    doc=doc.value
    doc=json.loads(doc)
    temp=json.loads(doc['events'])
    list_of_personal_events=[]
    for event in temp['data'] :
        try :
            int(event['id'])
        except :
            list_of_personal_events.append((event['name'], event['id']))
            
    return render_template("manageEvents.html", list_of_events=list_of_personal_events)

@app.route("/removeEvent", methods=['GET', 'POST'])
def removeEvent():
    doc=db.get(session['user_id'])
    doc=doc.value
    doc=json.loads(doc)
    pop=json.loads(doc['events'])
    temp=pop['data']
    list_of_personal_events=[]
    print(request.form['idToDelete'])
    for event in temp :
        if event['id']==request.form['idToDelete'] :
            temp.remove(event)

    pop['data']=temp
    doc['events']=json.dumps(pop)
    db.set(session['user_id'], json.dumps(doc))
    list_of_personal_events=[]

      
    eventsDays={}
    for event in temp :
        #print("lopp")
        #print(event)
        url="#"
        try :
            int(event['id'])
            url="https://www.facebook.com/events/"+event['id']
        except :
            url="#"
        if int(event['start_time'][8:10]) in eventsDays :
            temp_list_of_events=eventsDays[int(event['start_time'][8:10])]
            temp_list_of_events.append(((url, event['sentiment']), (int(event['start_time'][5:7]), (event['name']+"-"+event['start_time'][11:16]))))
            eventsDays[int(event['start_time'][8:10])]=temp_list_of_events
        else :
            temp_list_of_events=[]
            temp_list_of_events.append(((url, event['sentiment']), (int(event['start_time'][5:7]), (event['name']+"-"+event['start_time'][11:16]))))    
            eventsDays[int(event['start_time'][8:10])]=temp_list_of_events

        #print(eventsDays)
    global bDays
    bDays=eventsDays


    for event in temp :
        try :
            int(event['id'])
        except :
            list_of_personal_events.append((event['name'], event['id']))
            
    return render_template("manageEvents.html", list_of_events=list_of_personal_events)

@app.route("/addEvent", methods=['GET', 'POST'])
def addEvent():
    print("heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
    cal  = calendar.Calendar()
    year = time.localtime()[0]
    month = time.localtime()[1]
    days = cal.monthdatescalendar(year, month)    

    global bDays

    #Test for imporoper input

    isError=False
    if request.form['name']=="" :
        isError=True
    if request.form['start_time']=="" :
        isError=True
    if request.form['end_time']=="" :
        isError=True

    if isError :
        return render_template("calendar.html", days=days, bDays=bDays, inputError=True)

    if len(request.form['start_time'])<16 :
        the_start_time=request.form['start_time']+" 00:00:00"

    if len(request.form['end_time'])<16 :
        the_end_time=request.form['end_time']+" 00:00:00"

    doc=db.get(session['user_id'])
    doc=doc.value
    doc=json.loads(doc)
    print (doc['events'])
    pop=json.loads(doc['events'])
    temp=pop['data']
    print('HOOOOOOP'+json.dumps(temp))
    new_event = {}
    new_event["name"] = request.form["name"]
    new_event["id"] = request.form["name"]+request.form['start_time'] 
    new_event['start_time']=the_start_time
    new_event['end_time']=the_end_time
    temp_event=format_event(new_event)
    temp.append(format_event(new_event))
    pop['data']=temp
    doc['events']=json.dumps(pop)
    db.set(session['user_id'], json.dumps(doc))
    print("PLOP"+doc['events'])
    
    temp=bDays
    print("OYOYOY")
    print(request.form['start_time'])
    print(int(new_event['start_time'][8:10]))
   # print(temp[int(new_event['start_time'][8:10])])
    print(bDays)
    if int(new_event['start_time'][8:10]) in temp :
        temp_list_of_events=temp[int(new_event['start_time'][8:10])]
    else :
        temp_list_of_events=[]
    print(temp_list_of_events)
    temp_list_of_events.append((("#", temp_event['sentiment']), (int(request.form['start_time'][5:7]), (temp_event['name']+"-"+temp_event['start_time'][11:16]))))
    temp[int(new_event['start_time'][8:10])]=temp_list_of_events
    bdays=temp
    print("woah woah woah")
    print(bDays)
    return render_template("calendar.html", days=days, bDays=bDays, inputError=False)

@app.route("/logged_in", methods=['GET', 'POST'])
def logged_in():
    cal  = calendar.Calendar()

    year = time.localtime()[0]
    month = time.localtime()[1]

    days = cal.monthdatescalendar(year, month)

    session['logged_in']=True
    temp=""+request.form['user_info']
    user_info=json.loads(temp)
    print("one")
    del user_info['gender']
    del user_info['locale']
    del user_info['timezone']
    del user_info['verified']
    print("two")
    user_info['access_token']=request.form['access_token']
    print("wooahhh bufdyy0"+user_info['access_token'])
    user_id=user_info['id']
    try :
        #print("thtre")
        #print(request.form)
        session['user_id']=user_id
        #print("four") 
        db.add(user_id, json.dumps(user_info))
        #print("five")
        user_info['events']=get_fb_events(request.form['user_events'])
        #print("fellooowwww")
        temp=json.loads(user_info['events'])
        db.set(user_id, json.dumps(user_info))
        doc=db.get(user_id)
        doc=doc.value
        doc=json.loads(doc)
        temp=json.loads(doc['events'])
    except KeyExistsError:
        doc=db.get(user_id)
        doc=doc.value
        doc=json.loads(doc)
        del doc['access_token']
        doc['access_token']=user_info['access_token']
        #print("five")
        #print(request.form['user_events'])
        #print("six")
        doc['events']=updateEvents(request.form['user_events'], doc['events'])
        temp=json.loads(doc['events'])
        db.set(user_id, json.dumps(doc))
    eventsDays={}
    #print("ploppp")
    #print("LOLOLOLO"+temp)
    print(json.dumps(temp))
    print(type(temp['data']))
    for event in temp['data'] :
        #print("lopp")
        #print(event)
        url="#"
        try :
            int(event['id'])
            url="https://www.facebook.com/events/"+event['id']
        except :
            url="#"
        if int(event['start_time'][8:10]) in eventsDays :
            temp_list_of_events=eventsDays[int(event['start_time'][8:10])]
            temp_list_of_events.append(((url, event['sentiment']), (int(event['start_time'][5:7]), (event['name']+"-"+event['start_time'][11:16]))))
            eventsDays[int(event['start_time'][8:10])]=temp_list_of_events
        else :
            temp_list_of_events=[]
            temp_list_of_events.append(((url, event['sentiment']), (int(event['start_time'][5:7]), (event['name']+"-"+event['start_time'][11:16]))))    
            eventsDays[int(event['start_time'][8:10])]=temp_list_of_events

        #print(eventsDays)
    global bDays
    bDays=eventsDays
    return render_template("calendar.html", days=days, bDays=bDays, inputError=False)
@app.route("/")
def index() :
    user_id = session.get("user_id")
    
    #if not user_id :
    #   return render_template("login.html")
    #else:
    #   user = db.User.get_from_id(user_id)
        
    cal  = calendar.Calendar()
    
    year = time.localtime()[0]
    month = time.localtime()[1]
    days = cal.monthdatescalendar(year, month )
    global bDays
    #print(bDays)
    try:
        if (session['logged_in']) :
            return render_template("calendar.html", days =days, bDays=bDays, inputError=False)
        else:
            #print("fuck this")
            return render_template("login.html")
    except KeyError:
        #print("fuck er")
        return render_template("login.html")

if __name__ == "__main__" : 
    app.secret_key="secretive_key"
    app.run(debug=True)
    sess.init_app(app)
