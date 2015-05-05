from alchemyapi import AlchemyAPI

alchemyapi = AlchemyAPI()


def get_sentiment(post) :
	print ("in function")
	response = alchemyapi.sentiment("text", post)
	if response["status"] == "OK" :
		print ("here")
		if "score" in response["docSentiment"] :
			return {
				"score": float(response["docSentiment"]["score"]),
				"sentiment" : str(response["docSentiment"]["type"])
				}
		else :
			return {
				"score": float(0),
				"sentiment" : "Neutral"
				}
	else :
		print ("fuck, token must've expired")


print (get_sentiment("sometimes I feel very sad"))

print (get_sentiment("other times I love computer science!"))
