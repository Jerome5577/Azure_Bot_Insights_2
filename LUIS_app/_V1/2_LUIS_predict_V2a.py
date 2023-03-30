
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials

import json


# =====================================================================
# Authenticate prediction runtime client ------------------------------
# =====================================================================
app_id = "eba1db29-6ea2-4174-8949-eed43374d52d"
subscription_key = "8312b4570a6e44ac92cc24f8b5004067"
# Prediction
predictionKey = '8312b4570a6e44ac92cc24f8b5004067'
predictionEndpoint = 'https://luis-app-predicition.cognitiveservices.azure.com/'

runtimeCredentials = CognitiveServicesCredentials(predictionKey)
clientRuntime = LUISRuntimeClient(endpoint=predictionEndpoint, 
				  credentials=runtimeCredentials)


def predict(app_id, request , slot_name="Production"):
	# Example Query : predictionEndpoint/luis/prediction/v3.0/apps/app_id/slots/production/predict?verbose=true&show-all-intents=true&log=true&subscription-key=subscription_key&query=YOUR_QUERY_HERE

	# Note be sure to specify, using the slot_name parameter, whether your application is in staging or production.
	response = clientRuntime.prediction.get_slot_prediction(app_id=app_id, 
							 slot_name=slot_name, 
							 prediction_request=request)
	print("="*25)
	print(request)
	print("Top intent: {}".format(response.prediction.top_intent))
	#print("Sentiment: {}".format (response.prediction.sentiment))
	print("Intents: ")

	for intent in response.prediction.intents:
		print("\t{}".format (json.dumps (intent)))
	
	print("Entities: {}".format (response.prediction.entities))
	print("="*25)
	print()

request = { "query" : "Find flight to seattle" }
predict(app_id, request)

request = {"query" : "Find flight from Paris to Seattle"}
predict(app_id, request)

request = {"query" : "Hi I'd like to go to Caprica from Busan, between Sunday August 21, 2016 and Wednesday August 31, 2016"}
predict(app_id, request)

request = {"query" : "Hello"}
predict(app_id, request)

request = {"query" : "What time is it ?"}
predict(app_id, request)