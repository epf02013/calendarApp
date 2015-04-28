from alchemy import AlchemyAPI

alchemyapi = AlchemyAPI()


def get_sentiment(post) :
	response = alchemyapi.sentiment("text", post)
	if response["status"] == "OK" :
		if "score" in response["docSentiment"] :
			return {
				"score": float(response["docSentiment"]["score"]),
				"sentiment" : str(response["docSentiment"]["type"])
				}
	else :
		print "fuck, token must've expired"


print get_sentiment("sometimes I feel very sad")

print get_sentiment("other times I love computer science!")
