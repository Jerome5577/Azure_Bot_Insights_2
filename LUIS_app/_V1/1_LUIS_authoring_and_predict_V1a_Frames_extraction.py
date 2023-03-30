from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from functools import reduce

import json, time, uuid

# To Move To Config.py and put in gitignore
# from config import (authoringKey, authoringEndpoint, predictionEndpoint)
# Variables for keys and ressources---------------------------------
# Creation
authoringKey = '4c726694b8a3424b90fe3d7b639b5eac'
authoringEndpoint = 'https://p10-luis-app-creation.cognitiveservices.azure.com/'
# Prediction
#predictionKey = 'PASTE_YOUR_LUIS_PREDICTION_SUBSCRIPTION_KEY_HERE'
#predictionEndpoint = 'PASTE_YOUR_LUIS_PREDICTION_ENDPOINT_HERE'

def load_json(file_name):

    with open(file_name, "r") as f:
        return json.load(f)

def get_child_id(model, childName):

    theseChildren = next(filter((lambda child: child.name == childName), model.children))
    ChildId = theseChildren.id

    return ChildId

def get_grandchild_id(model, childName, grandChildName):
    
    theseChildren = next(filter((lambda child: child.name == childName), 
                                    model.children))
    theseGrandchildren = next(filter((lambda child: child.name == grandChildName), 
                                        theseChildren.children))
    
    grandChildId = theseGrandchildren.id
    
    return grandChildId

def quickstart():
    # =====================================================================
    # Define and create ---------------------------------------------------
    # =====================================================================
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
    #Created LUIS app with ID ae4adf76-027c-48c0-982a-997a461686f0

    # =====================================================================
    # Create intentions---------------------------------------------------
    # =====================================================================
    for intent in intentNames:
        client.model.add_intent(app_id, versionId, intent)

    # =====================================================================
    # Create entities ----------------------------------------------------
    # =====================================================================

    # ====================
    ## 1/ADD entities 
    # ====================
    ## Add pre_built entity
    ##--------------------------------
    client.model.add_prebuilt(app_id, versionId, 
                                prebuilt_extractor_names=["money", "geographyV2", 
                                                            "datetimeV2", "number", "ordinal"])
   
    ## Define entities from dataset
    ##--------------------------------
    #entity_keys = ['or_city', 'dst_city', 'str_date', 'end_date', 'budget']
    fromCityId = client.model.add_entity(app_id, versionId, name='or_city')
    toCityId = client.model.add_entity(app_id, versionId, name='dst_city')
    fromDateId = client.model.add_entity(app_id, versionId, name='str_date')
    toDateId = client.model.add_entity(app_id, versionId, name='end_date')
    budgetId = client.model.add_entity(app_id, versionId, name='budget')

    ## define machine-learned entity
    ##--------------------------------
    mlEntityDefinition = [
    {
        "name": "Flexible date",
        "children": [
            { "name": "around" }
        ]
    },
    {
        "name": "Price",
        "children": [
            { "name": "around" },
            { "name": "minimum" },
            { "name": "maximum" }       
        ]
    }
    ]
    ## add ML entity to app
    ##--------------------------------
    modelId = client.model.add_entity(app_id, versionId, name="Booking flight", 
                                        children=mlEntityDefinition)
    # ==========
    ### define phraselist - add phrases as significant vocabulary to app
    ###--------------------------------
    phraseList = {
        "enabledForAllModels": False,
        "isExchangeable": True,
        "name": "FlightPhraselist",
        "phrases": "cheaper, flexible, lowcost, direct, around, more ore less"
    }

    ### add phrase list to app
    phraseListId = client.features.add_phrase_list(app_id, versionId, 
                                                    phraseList)
    # ====================
    ## 2/Get entity and subentities
    # ====================
    ## ML Entity
    modelObject = client.model.get_entity(app_id, versionId, modelId)
    ## Dataset Entities
    fromCityObject = client.model.get_entity(app_id, versionId, fromCityId)
    toCityObject = client.model.get_entity(app_id, versionId, toCityId)
    fromDateObject = client.model.get_entity(app_id, versionId, fromDateId)
    toDateObject = client.model.get_entity(app_id, versionId, toDateId)
    budgetObject = client.model.get_entity(app_id, versionId, budgetId)
    ## ML Subentities    
    flexibleDateId = get_grandchild_id(modelObject, "Flexible date", "around")
    aroundPriceId = get_grandchild_id(modelObject, "Price", "around")
    miniPriceId = get_grandchild_id(modelObject, "Price", "minimum")
    maxPriceId = get_grandchild_id(modelObject, "Price", "maximum")

    # ====================
    ### 3/Add model as feature
    ### ====================
    
    ### Add model as feature to subentity model
    ## Geo
    prebuiltFeaturedDefinition = {"model_name" : "geographyV2", "is_required": False}
    client.features.add_entity_feature(app_id, versionId, fromCityObject, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, toCityObject, prebuiltFeaturedDefinition)
    ## Date
    prebuiltFeaturedDefinition = {"model_name": "datetimeV2", "is_required": False}
    client.features.add_entity_feature(app_id, versionId, fromDateObject, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, toDateObject, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, flexibleDateId, prebuiltFeaturedDefinition)
    ## Budget
    prebuiltFeaturedDefinition = {"model_name": "money", "is_required": False}
    client.features.add_entity_feature(app_id, versionId, budgetObject, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, aroundPriceId, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, miniPriceId, prebuiltFeaturedDefinition)
    client.features.add_entity_feature(app_id, versionId, maxPriceId, prebuiltFeaturedDefinition)
    
    # ==========
    # phrase list as feature 
        # to entity
    phraseListFeatureDefinition = { "feature_name": "FlightPhraselist", "model_name": None }
    client.features.add_entity_feature(app_id, versionId, fromCityObject, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, toCityObject, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, fromDateObject, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, toDateObject, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, budgetObject, phraseListFeatureDefinition)
        # to subentity model
    client.features.add_entity_feature(app_id, versionId, flexibleDateId, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, aroundPriceId, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, miniPriceId, phraseListFeatureDefinition)
    client.features.add_entity_feature(app_id, versionId, maxPriceId, phraseListFeatureDefinition)


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
    #client.examples.add(app_id, versionId, labeledExampleUtteranceWithMLEntity, { "enableNestedChildren": True })

    # =====================================================================
    # Train the model ---------------------------------------------------------
    # =====================================================================
    client.train.train_version(app_id, versionId)
    waiting = True
    while waiting:
        info = client.train.get_status(app_id, versionId)

        # get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
        waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
        if waiting:
            print ("Waiting 10 seconds for training to complete...")
            time.sleep(10)
        else: 
            print ("trained")
            waiting = False

    # =====================================================================
    # Publish the app -----------------------------------------------------
    # =====================================================================
    # Mark the app as public so we can query it using any prediction endpoint.
    # Note: For production scenarios, you should instead assign the app to your own LUIS prediction endpoint. See:
    # https://docs.microsoft.com/en-gb/azure/cognitive-services/luis/luis-how-to-azure-subscription#assign-a-resource-to-an-app
    client.apps.update_settings(app_id, is_public=True)

    responseEndpointInfo = client.apps.publish(app_id, versionId, is_staging=False)

'''

    # =====================================================================
    # Authenticate prediction runtime client ------------------------------
    # =====================================================================
    runtimeCredentials = CognitiveServicesCredentials(predictionKey)
    clientRuntime = LUISRuntimeClient(endpoint=predictionEndpoint, credentials=runtimeCredentials)

    # =====================================================================
    # Get a prediction from runtime ---------------------------------------
    # =====================================================================

    # Production == slot name
    predictionRequest = {"query": "Hi. i'd like to fly from Paris to Marseille on May 5, 2023"}

    predictionResponse = clientRuntime.prediction.get_slot_prediction(app_id, "Production", predictionRequest)
    print(f"Top intent : {predictionResponse.prediction.top_intent}")
    print(f"Sentiment : {predictionResponse.prediction.sentiment}")

    for intent in predictionResponse.prediction.intents:
        print(f"\t{json.dumps(intent)}")
    print(f"Entities : {predictionResponse.prediction.entities}")

'''

quickstart()