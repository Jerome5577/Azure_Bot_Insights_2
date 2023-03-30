
# https://github.com/Azure-Samples/cognitive-services-quickstart-code/blob/master/python/LUIS/python-sdk-authoring-prediction/application_quickstart.py

from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from msrest.authentication import CognitiveServicesCredentials

import datetime, json, os, time

def load_json(file_name):
    with open(file_name, "r+b") as f:
        return json.load(f)

# =====================================================================
# Variables for keys and ressources------------------------------------
# =====================================================================
# Creation
authoring_key = '4c726694b8a3424b90fe3d7b639b5eac'
authoring_endpoint = 'https://p10-luis-app-creation.cognitiveservices.azure.com/'
intentName = 'bookFlight'
# Instantiate a LUIS client
client = LUISAuthoringClient(authoring_endpoint, 
                             CognitiveServicesCredentials(authoring_key))

# =====================================================================
# Create app ----------------------------------------------------------
# =====================================================================
def create_app():
	# Create a new LUIS app
	app_name    = "FlyMe LUISapp test1 {}".format(datetime.datetime.now())
	app_desc    = "Flight booking app built with LUIS Python SDK."
	app_version = "0.1"
	app_locale  = "en-us"

	app_id = client.apps.add(dict(name=app_name,
									initial_version_id=app_version,
									description=app_desc,
									culture=app_locale))

	print("Created LUIS app {}\n    with ID {}".format(app_name, app_id))
	return app_id, app_version

# =====================================================================
# Create intents (intentions)------------------------------------------
# =====================================================================
# Declare an intent, FindFlights, that recognizes a user's Flight request
# Creating an intent returns its ID, which we don't need, so don't keep.
def add_main_intent(app_id, app_version, intentName):
	intentId = client.model.add_intent(app_id, app_version, intentName)
	print("Intent {} {} added.".format(intentName, intentId) )
	
def add_other_intents(app_id, app_version):
	intentNames = ["confirm", "greetings", "none"]
	
	for intent in intentNames :
		intentId = client.model.add_intent(app_id, app_version, intent)
		print("Intent {} {} added.".format(intent, intentId))
	
# =====================================================================
# Create entities ----------------------------------------------------
# =====================================================================
# Creating an entity (or other LUIS object) returns its ID.
# We don't use IDs further in this script, so we don't keep the return value.
def add_entities(app_id, app_version):

    ## Add pre_built entity
    ##--------------------------------
    client.model.add_prebuilt(app_id, app_version, 
                                prebuilt_extractor_names=["money", "geographyV2", 
                                                            "datetimeV2", "number", "ordinal"])
   
    ## Define entities from dataset
    ##--------------------------------
    entity_keys = ['or_city', 'dst_city', 'str_date', 'end_date', 'budget']
    for key in entity_keys : 
        key_name = key
        entity_id = client.model.add_entity(app_id, app_version, name=key_name)
        modelObject = client.model.get_entity(app_id, app_version, entity_id)
        print("{} simple entity created with id {}".format(key_name, entity_id))
        
# =====================================================================
# Add phraselist - add phrases as significant vocabulary to app -------
# =====================================================================
def add_phraseList(app_id, app_version):
    phraseList = {
        "enabledForAllModels": False,
        "isExchangeable": True,
        "name": "FlightPhraselist",
        "phrases": "cheaper, flexible, lowcost, direct, around, more ore less"
    }

    ### add phrase list to app
    phraseListId = client.features.add_phrase_list(app_id, app_version, 
                                                    phraseList)

# =====================================================================
# Add utterances ------------------------------------------------------
# =====================================================================
def add_first_test_utterance(app_id, app_version, intentName):
	# Now define the utterances
    uterrance_test = {
		'text': "Hi I'd like to go to Caprica from Busan, between Sunday August 21, 2016 and Wednesday August 31, 2016", 
        'intentName': intentName, 
        'entityLabels': 
            [
          	{'startCharIndex': 21, 
               	'endCharIndex': 28,
          		'entityName': 'dst_city'}, 
        	{'startCharIndex': 34, 
              	'endCharIndex': 39,
          		'entityName': 'or_city'}, 
            {'startCharIndex': 49, 
                'endCharIndex': 71,
          		'entityName': 'str_date'
             	}, 
            {'startCharIndex': 76, 
                'endCharIndex': 101,
          		'entityName': 'end_date'}
            ]
	}
    
    client.examples.add(app_id, app_version, uterrance_test)
    print("Test example utterance added : ", uterrance_test)
	   
def add_utterances_for_bookFlight(app_id, app_version):
    # Now define the utterances
	bookFlight_json_file = "./datas/json_frame_25Utterrances_for_first_training.json"
	bookFlight_utterances = load_json(bookFlight_json_file)

	print("\nFirst BookFlight_utterances exemple : ", bookFlight_utterances[0])
	client.examples.batch(app_id, app_version, bookFlight_utterances)
	
	'''
	for utterance in bookFlight_utterances:
		print("\nUtterance : ", utterance)
		client.examples.add(app_id, app_version, utterance)
	'''

def add_utterances_for_confirm(app_id, app_version):
	# Now define the utterances for 'confirm'
    confirm_uterrances = [
    	{
            "text": "right",
            "intentName": "confirm",
      		"entityLabels": []
        },
    	{
            "text": "Ok, that's fine",
            "intentName": "confirm",
      		"entityLabels": []
        },       
        {
            "text": "yes",
            "intentName": "confirm",
      		"entityLabels": []
        },
    	{
            "text": "That's goo for me",
            "intentName": "confirm",
      		"entityLabels": []
        }
	]
    
    client.examples.batch(app_id, app_version, confirm_uterrances)
    print("Test example confirm utterance added : ", confirm_uterrances)
    
def add_utterances_for_greetings(app_id, app_version):
	# Now define the utterances for 'greetings'
    greetings_uterrances = [
	    {
            "text": "Good morning",
            "intentName": "greetings",
      		"entityLabels": []
        },
        {
            "text": "Hello, how are you ?",
            "intentName": "greetings",
      		"entityLabels": []
        },
        {
            "text": "Hi",
            "intentName": "greetings",
      		"entityLabels": []
        },
        {
            "text": "Hello",
            "intentName": "greetings",
      		"entityLabels": []
        }
	]
    	
    client.examples.batch(app_id, app_version, greetings_uterrances)
    print("Test example greetings utterance added : ", greetings_uterrances)

def add_utterances_for_None(app_id, app_version):
	# Now define the utterances for 'greetings'
    none_uterrance = [
    	{
            "text": "What time is it?",
            "intentName": "none",
      		"entityLabels": []
        },      
		{
            "text": "I would like a sandwich",
            "intentName": "none",
      		"entityLabels": []
        }, 
        {
            "text": "My sister is travelling to the USA for christmas",
            "intentName": "none",
      		"entityLabels": []
        }, 
        {
            "text": "Is paris far from here ?",
            "intentName": "none",
      		"entityLabels": []
        }
	]
    
    client.examples.batch(app_id, app_version, none_uterrance)
    print("Test example greetings utterance added : ", none_uterrance)
    
# =====================================================================
# Train model ---------------------------------------------------------
# =====================================================================
def train_app(app_id, app_version):
	response = client.train.train_version(app_id, app_version)
	waiting = True
	while waiting:
		info = client.train.get_status(app_id, app_version)

		# get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
		waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
		if waiting:
			print ("Waiting 10 seconds for training to complete...")
			time.sleep(10)

# =====================================================================
# Publish app ---------------------------------------------------------
# =====================================================================
def publish_app(app_id, app_version):
	responseEndpointInfo = client.apps.publish(app_id, app_version, is_staging=True)
	print("Application published. Endpoint URL: " + responseEndpointInfo.endpoint_url)
	
# ==========================================================================================================================================
# Loading 
# =====================================================================
print("Creating application...")
app_id, app_version = create_app()
print()

print ("Adding entities to application...")
add_entities(app_id, app_version)
print ()

print ("Adding phraseList to application...")
add_phraseList(app_id, app_version)
print ()

print ("Adding intents to application...")
add_main_intent(app_id, app_version, intentName)
print ()
print ("Adding intents to application...")
add_other_intents(app_id, app_version)
print ()

#print ("Adding first test utterance to application...")
#add_first_test_utterance(app_id, app_version, intentName)
#print ()
print ("Adding utterances for main intent bookFliht to application...")
add_utterances_for_bookFlight(app_id, app_version)
print ()
print ("Adding utterances for confirm intent to application...")
add_utterances_for_confirm(app_id, app_version)
print ()
print ("Adding utterances for greetings intent to application...")
add_utterances_for_greetings(app_id, app_version)
print ()
print ("Adding utterances for None intent to application...")
add_utterances_for_None(app_id, app_version)
print ()

print ("Training application...")
train_app(app_id, app_version)
print ()

print ("Publishing application...")
publish_app(app_id, app_version)
print ()

'''
# Clean up resources.
print ("Deleting application...")
client.apps.delete(app_id)
print ("Application deleted.")
'''