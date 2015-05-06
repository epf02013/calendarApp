import datetime, calendar, json, time               # utility libraries
from couchbase.bucket import Bucket                 # we need this to link up to the DB 
from couchbase.exceptions import KeyExistsError, NotFoundError
from couchbase.views.params import Query
from fb_grabber import get_fb_events, updateEvents, format_event       
from flask import Flask, render_template, request, session, redirect, url_for
from models import user, dbName                           # M in MVC

# useful variables 
url_sentiment_startTime_name={}

# create the app lazily 
app = Flask(__name__)


# connect to Couchbase 
def connect_db():
    return Bucket(dbName)
db=connect_db()

#Login Page 
@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("login.html")

#Logout Page
@app.route("/logout", methods=['GET', 'POST'])
def logout():

    # Change the session variable which is responsive on all pages
    session['logged_in']=False
    return render_template("logout.html")

#Page for Managing Events 
@app.route("/manageEvents")
def manageEvents():

    #Load Users documents 
    doc=db.get(session['user_id'])
    doc=doc.value
    doc=json.loads(doc)
    #Gets users events
    temp=json.loads(doc['events'])
    list_of_personal_events=[]    #List to store personal events
    for event in temp['data'] :
        try :
        #If the id is an int then it Is A facebook Event and shouldnt be added
            int(event['id'])      
        except :
            #Must be a personal event so add to list 
            list_of_personal_events.append((event['name'], event['id'])) 
        #Return a rendering of managing events page
    return render_template("manageEvents.html", list_of_events=list_of_personal_events)

#Removes event passed in by post and returns rendering of managing page
@app.route("/removeEvent", methods=['GET', 'POST'])
def removeEvent():
    if not request.method=="POST" :
        return render_template("404.html"), 404


#Load Users document
    doc=db.get(session['user_id'])
    doc=doc.value
    doc=json.loads(doc)
#Load Users Events
    pop=json.loads(doc['events'])
    temp=pop['data']
    list_of_personal_events=[]
    print(request.form['idToDelete'])
#Iterates through events testing for ID equality removes Event with matching ID 
    for event in temp :
        if event['id']==request.form['idToDelete'] :
            temp.remove(event)

#Update Users events in Documents
    pop['data']=temp
    doc['events']=json.dumps(pop)
    db.set(session['user_id'], json.dumps(doc))

#Updates url_sentiment_startTime-name list of events for the Calendar Page
    eventsDays={}
    for event in temp :
        url="#"
        try :
            #If the events ID is a number then it is a Facebook event and should have a link
            int(event['id'])     
            url="https://www.facebook.com/events/"+event['id']
        except :
            url="#"
        if int(event['start_time'][8:10]) in eventsDays :     #If there is already an event on this day append to list
            temp_list_of_events=eventsDays[int(event['start_time'][8:10])]
            temp_list_of_events.append(((url, event['sentiment']), (int(event['start_time'][5:7]), (event['name']+"-"+event['start_time'][11:16]))))
            eventsDays[int(event['start_time'][8:10])]=temp_list_of_events
        else :
            #If this is the first event on the day, create list and place event in it
            temp_list_of_events=[]
            temp_list_of_events.append(((url, event['sentiment']), (int(event['start_time'][5:7]), (event['name']+"-"+event['start_time'][11:16]))))    
            eventsDays[int(event['start_time'][8:10])]=temp_list_of_events

    global url_sentiment_startTime_name
    url_sentiment_startTime_name=eventsDays

#Updates list of personal events for the managing page
    list_of_personal_events=[]     
    for event in temp :
        try :
            int(event['id'])
        except :
            list_of_personal_events.append((event['name'], event['id']))
            
    return render_template("manageEvents.html", list_of_events=list_of_personal_events)


#Adds an event to Users events
@app.route("/addEvent", methods=['GET', 'POST'])
def addEvent():
    if not request.method=="POST" :
        return render_template("404.html"), 404


    # add a new event given a date, time, event name

    # use the calendar library for calendar manipulation
    cal  = calendar.Calendar()
    year = time.localtime()[0]
    month = time.localtime()[1]
    days = cal.monthdatescalendar(year, month)    

    global url_sentiment_startTime_name

    #Test for imporoper input 
    isError=False
    if request.form['name']=="" :
        isError=True
    if request.form['start_time']=="" :
        isError=True
    if request.form['end_time']=="" :
        isError=True
    the_end_time=request.form['end_time']
    the_start_time=request.form['start_time']
    if isError :  
        # If input is incorrect do not add event. Return rendering of calendar with error message and 
        return render_template("calendar.html", days=days, url_sentiment_startTime_name=url_sentiment_startTime_name, inputError=True)

    if len(request.form['start_time'])<16 :
        #If user forgot to add hour to start time add automatic time
        the_start_time=request.form['start_time']+" 00:00:00"
        #If user forgot to add hour to end time add automatic time
    if len(request.form['end_time'])<16 :
        the_end_time=request.form['end_time']+" 01:00:00"

    #print('HOOOOOOP'+json.dumps(temp))
#form the new Event from request form    
    new_event = {}
    new_event["name"] = request.form["name"]
    new_event["id"] = request.form["name"]+request.form['start_time'] 
    new_event['start_time']=the_start_time
    new_event['end_time']=the_end_time
    temp_event=format_event(new_event)

#Load User Document
    doc = db.get(session['user_id'])
    doc = doc.value
    doc = json.loads(doc)
#Load User Events     
    pop = json.loads(doc['events'])
    temp = pop['data']
    
#add event to User events
    temp.append(format_event(new_event))
    pop['data']=temp
    doc['events']=json.dumps(pop)
#Update User document with new events
    db.set(session['user_id'], json.dumps(doc))
    #print("PLOP"+doc['events'])

    
    temp=url_sentiment_startTime_name
    if int(new_event['start_time'][8:10]) in temp :
        #If there are events on this day load them into temp_list
        temp_list_of_events=temp[int(new_event['start_time'][8:10])]
    else :
        #there are no evenets on this day yet so make temp_list empty
        temp_list_of_events=[]
#Add new event to url_sentiment_startTime_name
    temp_list_of_events.append((("#", temp_event['sentiment']), (int(request.form['start_time'][5:7]), (temp_event['name']+"-"+temp_event['start_time'][11:16]))))
    temp[int(new_event['start_time'][8:10])]=temp_list_of_events
    url_sentiment_startTime_name=temp
#Return rendering of calendar page with updated events
    return render_template("calendar.html", days=days, url_sentiment_startTime_name=url_sentiment_startTime_name, inputError=False)


#Handles users logging in and returns rendering of calendar page 
@app.route("/logged_in", methods=['GET', 'POST'])
def logged_in():
    if not request.method=="POST" :
        return render_template("404.html"), 404


    # calendar manipulation
    cal  = calendar.Calendar()
    year = time.localtime()[0]
    month = time.localtime()[1]
    days = cal.monthdatescalendar(year, month)

    # logged_in session variable is now T
    session['logged_in']=True
    temp=str(request.form['user_info'])
    user_info=json.loads(temp)
    
    # Some of the stuff facebook returns is irrelevant to calendar, so we delete it 
    # so it doesn't waste space in the database 
    del user_info['gender']
    del user_info['locale']
    del user_info['timezone']
    del user_info['verified']
    

    user_info['access_token'] = request.form['access_token']
    user_id=user_info['id']
    try :
        #Try adding user to database. Will throw KeyExistsError if user is already in the database
        session['user_id'] = user_id
        db.add(user_id, json.dumps(user_info))
        # try to get facebook events 
        user_info['events'] = get_fb_events(request.form['user_events'])
        temp = json.loads(user_info['events'])
        db.set(user_id, json.dumps(user_info))
    except KeyExistsError:
        #catches the KeyExistsError and so must be existing User so updates their information
        #Load Users Document
        doc = db.get(user_id)
        doc = doc.value
        doc = json.loads(doc)
        #delete old Facebook access token
        del doc['access_token']
        #update Users access token
        doc['access_token'] = user_info['access_token']
        #updates users events with the events retrieved from facebook
        doc['events'] = updateEvents(request.form['user_events'], doc['events'])
        temp = json.loads(doc['events'])
        db.set(user_id, json.dumps(doc))


#Sets the events in url_sentiment_startTime_name  list
    eventsDays={}
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
    global url_sentiment_startTime_name
    url_sentiment_startTime_name=eventsDays

    #returns rendering of calendar Page
    return render_template("calendar.html", days=days, url_sentiment_startTime_name=url_sentiment_startTime_name)

#@app.route("/manager", methods=["GET", "POST"])
#def manager():
    
#    if session.get("isAdmin") :
#        q = Query
#        q.limit = 100
#        q.skip = 1
#        users = {"tim": "timkaye", "ethan" : "ethanCaleb"}
#        return render_template("manager.html", users=users)
#    else :
#        return render_template("login.html")

#    if request.method == "POST": 
#        # Oh, we got a post request
#        userToDelete = str(request.form["deleteID"])
#        try: 
#            db.delete(userToDelete)
#        except KeyExistsError :
#            print "Couldn't delete userID: %s" % userToDelete

#        return render_template("manager.html")


#Home page returns rendering of calendar if logged in otherwise redirects to Login
@app.route("/")
def index() :
    user_id = session.get("user_id")
    
    # calendar stuff
    cal  = calendar.Calendar()
    year = time.localtime()[0]
    month = time.localtime()[1]
    days = cal.monthdatescalendar(year, month )
    global url_sentiment_startTime_name

    try:
        if (session['logged_in']) :
            return render_template("calendar.html", days =days, url_sentiment_startTime_name=url_sentiment_startTime_name, inputError=False)
        else:
            return render_template("login.html")
    except KeyError:
        return render_template("login.html")

# handle error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404



# this is where we run the app!
if __name__ == "__main__" : 
    app.secret_key="secretive_key"
    app.run(debug=True)
    sess.init_app(app)
