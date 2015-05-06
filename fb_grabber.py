import json
import requests
import arrow
import datetime
import time
from classifier import get_sentiment


#takes stored events and returns old events + new events as json
def updateEvents(response, prevEvents) :
    eventsFromFB = json.loads(get_fb_events(response))
    prevEvents = json.loads(prevEvents)
    for fbEvent in eventsFromFB['data'] :
        isNew=True
        for prevEvent in prevEvents['data'] :
            if fbEvent['id']==prevEvent['id'] :
                isNew=False
        if isNew :
            prevEvents['data'].append(format_event(fbEvent))
    return json.dumps(prevEvents)

        
        
# facebook data extract 
def get_fb_events(response) :
    # store all events in an array
    events = {}
    events['data']=[]
   
    # datetime stuff
    year = time.localtime()[0]
    month = time.localtime()[1]

    # load the response data
    resp_body =json.loads(response)
    if "data" in resp_body.keys() : 
        for event in resp_body["data"] :
            # we only care about events that you plan on attending
            if event["rsvp_status"] == "attending" :
                if (int(event['start_time'][:4])==year and int(event['start_time'][5:7])==month) :
                    events['data'].append(format_event(event))
            
            # check for events on the second page 
            if "paging" in resp_body.keys() :
                if "next" in resp_body["paging"].keys() :
                    next_page = requests.get(resp_body["paging"]["next"])
                    if next_page.status_code == requests.codes.ok :
                        month = datetime.datetime.now().month
                        for event in next_page.json()["data"] :
                            if (arrow.get(event["start_time"]).month == month and arrow.get(event["start_time"]).year==year) :
                                events['data'].append(format_event(event))
                        
    return json.dumps(events)


def format_event(event) :
    if event:
        new_event = {}
        new_event["name"] = event["name"]
        new_event["id"] = event["id"]
        new_event["start_time"] = arrow.get(event["start_time"]).format("YYYY-MM-DD HH:mm:ss")
        if "end_time" in event.keys(): 
            new_event["end_time"] = arrow.get(event["end_time"]).format("YYYY-MM-DD HH:mm:ss")

        # now add the document sentiment stuff
        response = get_sentiment(str(event["name"]))
        if response :
            if "score" in response.keys():
                new_event["score"] = response["score"]
                new_event["sentiment"] = response["sentiment"]
    
    return new_event
