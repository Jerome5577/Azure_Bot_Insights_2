

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
# Existed app
app_id = "eba1db29-6ea2-4174-8949-eed43374d52d"
app_version = "0.1"

# =====================================================================
# Add utterances ------------------------------------------------------
# =====================================================================
def add_utterances_for_bookFlight(app_id, app_version):
    # Now define the utterances
    bookFlight_json_file = "./datas/json_frame_Utterrances_for_complete_training.json"
    bookFlight_utterances = load_json(bookFlight_json_file)
	
    #print("\nFirst BookFlight_utterances exemple : ", bookFlight_utterances[0])
    #client.examples.batch(app_id, app_version, bookFlight_utterances)

    # Sending trainset by batches of 50 conversations :    
    for n in range((len(bookFlight_utterances)//50)-1) : 
        i = 50 * n
        client.examples.batch(app_id, app_version, bookFlight_utterances[i:i+50])
        time.sleep(0.2)
	
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

# ==========================================================================================================================================
# Loading 
# =====================================================================
print ("Adding utterances for main intent bookFliht to application...")
add_utterances_for_bookFlight(app_id, app_version)
print ()

print ("Training application...")
train_app(app_id, app_version)
print ()