import json
import requests
import arrow
import datetime
from config import FB_ACCESS_TOKEN
from classifier import get_sentiment

# facebook data extract 
def get_fb_events(user_id) :
	# store all events in an array
	events = []

	# the base URL to query
	url = "https://graph.facebook.com/v2.3/%s/events?access_token=%s&pretty=1" % (user_id, FB_ACCESS_TOKEN)

	# make a GET 
	response = requests.get(url)
	if response.status_code == requests.codes.ok :
		# decode the JSON
		resp_body = response.json()
		if "data" in resp_body.keys() : 
			for event in resp_body["data"] :
				# we only care about events that you plan on attending
				if event["rsvp_status"] == "attending" :
					events.append(format_event(event))

		# check for events on the second page 
		if "paging" in resp_body.keys() :
			if "next" in resp_body["paging"].keys() :
				next_page = requests.get(resp_body["paging"]["next"])
				if next_page.status_code == requests.codes.ok :
					month = datetime.datetime.now().month
					for event in next_page.json()["data"] :
						if arrow.get(event["start_time"]).month == month :
							events.append(format_event(event))
	else :
		print "access code expired :("

	return json.dumps(events)


def format_event(event) :
	new_event = {}
	new_event["name"] = event["name"]
	new_event["event_id"] = event["id"]
	new_event["start_time"] = arrow.get(event["start_time"]).format("YYYY-MM-DD HH:mm:ss")
	if "end_time" in event.keys(): 
		new_event["end_time"] = arrow.get(event["end_time"]).format("YYYY-MM-DD HH:mm:ss")

	# now add the document sentiment stuff
	response = get_sentiment(str(event["name"]))
	new_event["score"] = response["score"]
	new_event["sentiment"] = response["sentiment"]
	
	return new_event



if __name__ == "__main__" :
	print get_fb_events("10152889999328269")
