from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from functools import reduce

import json, time, uuid

# To Move To Config.py and put in gitignore
# from config import (authoringKey, authoringEndpoint, predictionEndpoint)
# Variables for keys and ressources---------------------------------
authoringKey = 'PASTE_YOUR_LUIS_AUTHORING_SUBSCRIPTION_KEY_HERE'
authoringEndpoint = 'PASTE_YOUR_LUIS_AUTHORING_ENDPOINT_HERE'
predictionKey = 'PASTE_YOUR_LUIS_PREDICTION_SUBSCRIPTION_KEY_HERE'
predictionEndpoint = 'PASTE_YOUR_LUIS_PREDICTION_ENDPOINT_HERE'

def load_json(file_name):

    with open(file_name, "r") as f:
        return json.load(f)

def get_grandchild_id(model, childName, grandChildName):
    
    theseChildren = next(filter((lambda child: child.name == childName), 
                                    model.children))
    theseGrandchildren = next(filter((lambda child: child.name == grandChildName), 
                                        theseChildren.children))
    
    grandChildId = theseGrandchildren.id
    
    return grandChildId

def quickstart():
    # We use a UUID to avoid name collisions----------------------------
    appName = "Fly Me " + str(uuid.uuid4())
    versionId = "0.1"
    intentNames = ["bookFlight", "confirm", "greetings"]

    # Authenticate client------------------------------------------------
    client = LUISAuthoringClient(authoringEndpoint, 
                                    CognitiveServicesCredentials(authoringKey))

    # Create LUIS application -------------------------------------------
    # define app basics
    appDefinition = ApplicationCreateObject (name=appName, 
                                                initial_version_id=versionId, 
                                                culture='en-us')

    # create app
    app_id = client.apps.add(appDefinition)

    # get app id - necessary for all other changes
    print("Created LUIS app with ID {}".format(app_id))

    # Create intentions---------------------------------------------------
    for intent in intentNames:
        client.model.add_intent(app_id, versionId, intent)

    # Create entities ----------------------------------------------------
    # Add pre_built entity
    client.model.add_prebuilt(app_id, versionId, 
                                prebuilt_extractor_names=["money", "geographyV2", 
                                                            "datetimeV2", "number", "ordinal"])
    # ==========
    ## define machine-learned entity
    mlEntityDefinition = [
    
    
    {
        "name": "Travel",
        "children": [
            { "name": "or_city" },
            { "name": "dst_city" }
        ]
    },
    {
        "name": "Date",
        "children": [
            { "name": "str_date" },
            { "name": "end_date" }
        ]
    },
    

    {
        "name": "Budget",
        "children": [
            { "name": "Minimum" },
            { "name": "Maximum" }
        ]
    }
    ]
    ## add ML entity to app
    modelId = client.model.add_entity(app_id, versionId, name="Booking flight", 
                                        children=mlEntityDefinition)

    # ==========
    ### define phraselist - add phrases as significant vocabulary to app
    phraseList = {
        "enabledForAllModels": False,
        "isExchangeable": True,
        "name": "FlightPhraselist",
        "phrases": "cheaper,flexible,lowcost,direct"
    }
    ### add phrase list to app
    phraseListId = client.features.add_phrase_list(app_id, versionId, 
                                                    phraseList)

    # ==========
    # Get entity and subentities
    ## Entity
    modelObject = client.model.get_entity(app_id, versionId, modelId)
    ## Subentities
    
    airportFromId = get_grandchild_id(modelObject, "Airport", "or_city")
    airportToId = get_grandchild_id(modelObject, "Airport", "dst_city")
    dateDepartureId = get_grandchild_id(modelObject, "Date", "str_date")
    dateReturnId = get_grandchild_id(modelObject, "Date", "end_date")
    
    miniBudgetId = get_grandchild_id(modelObject, "Budget", "Minimum")
    maxBudgetId = get_grandchild_id(modelObject, "Budget", "Maximum")

     # ==========
    # Add model as feature to subentity model
    ## Airport
    prebuiltFeaturedDefinition = {"model_name" : "geographyV2", "is_required": False}
    client.features.add_entity_feature(app_id, versionId, airportFromId, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, airportToId, prebuiltFeaturedDefinition)
    ## Date
    prebuiltFeaturedDefinition = {"model_name": "datetimeV2", "is_required": False}
    client.features.add_entity_feature(app_id, versionId, dateDepartureId, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, dateReturnId, prebuiltFeaturedDefinition)
    ## Budget
    prebuiltFeaturedDefinition = {"model_name": "money", "is_required": False}
    client.features.add_entity_feature(app_id, versionId, miniBudgetId, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, maxBudgetId, prebuiltFeaturedDefinition)
    # ==========
    # add phrase list as feature to subentity model
    phraseListFeatureDefinition = { "feature_name": "FlightPhraselist", "model_name": None }
    client.features.add_entity_feature(app_id, versionId, airportFromId, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, airportToId, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, dateDepartureId, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, dateReturnId, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, miniBudgetId, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, maxBudgetId, phraseListFeatureDefinition)

    # Add utterances examples to intents ----------------------------------------------
    # Define labeled examples
    bookFlight_json_file = "./datas/json_frame_for_first_training.json"
    bookFlight_utterance = load_json(bookFlight_json_file)
    print("\nBookFlight_utterance : ", bookFlight_utterance)

    other_utterances = [
        {
            "text": "right",
            "intentName": intentNames[1]
        },
        {
            "text": "yes",
            "intentName": intentNames[1]
        },
        {
            "text": "OK",
            "intentName": intentNames[1]
        },{
            "text": "good",
            "intentName": intentNames[1]
        },
        {
            "text": "Hello",
            "intentName": intentNames[2]
        },
        {
            "text": "Hi",
            "intentName": intentNames[2]
        },
        {
            "text": "Hey",
            "intentName": intentNames[2]
        },
        {
            "text": "Good morning",
            "intentName": intentNames[2]
        }
    ]
    
    '''
    # Define labeled example for ML Entity
    labeledExampleUtteranceWithMLEntity = {
        "text": "I would like a vacation for one in Mannheim from August 17 to September 7. My city of departure is Porto Alegre. It should cost less than $3000.",
        "intentName": "bookFLight",
        "entity_labels": [
            {
                "entity_name": "dst_city",
                "start_char_index": 35,
                "end_char_index": 43
            },
            {
                "entity_name": "str_date",
                "start_char_index": 49,
                "end_char_index": 58
            },
            {
                "entity_name": "end_date",
                "start_char_index": 62,
                "end_char_index": 73
            },
            {
                "entity_name": "or_city",
                "start_char_index": 99,
                "end_char_index": 111
            },
            {
                "entity_name": "budget",
                "start_char_index": 138,
                "end_char_index": 143
            }
        ]
    }
    '''

    # Add an example for the entity
    # Enable nested children to allow using multiple models with the same name
    # The "quantity" subentity and the phraselise could have the same exact name if this is set to True
    for utterance in bookFlight_utterance:
        print("\nutterance : ", utterance)
        client.examples.add(app_id, versionId, utterance, {"enableNestedChildren": True})
    # Other entities
    for utterance in other_utterances:
        client.examples.add(app_id, versionId, utterance, {"enableNestedChildren": False})
    # ML Entity
    client.examples.add(app_id, versionId, labeledExampleUtteranceWithMLEntity, { "enableNestedChildren": True })
