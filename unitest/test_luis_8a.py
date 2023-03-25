from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials

from bot_config import DefaultConfig

CONFIG = DefaultConfig()

# Instantiate prediction client
client_runtime = LUISRuntimeClient(
        CONFIG.LUIS_API_HOST_NAME,
        CognitiveServicesCredentials(CONFIG.LUIS_API_KEY))

# intentNames = ["confirm", "greetings", "none", 'bookFlight']


def test_greetings_intent():
    # Create request
    test_request = "Hello"
    # Get response
    test_response = client_runtime.prediction.resolve(CONFIG.LUIS_APP_ID, query=test_request)

    expected_intent = "greetings"
    actual_intent = test_response.top_scoring_intent.intent
    
    print('Test Greetings intent :')
    print('-'*22)
    assert actual_intent == expected_intent
    print('Query :', test_request)
    print('Expected intent :', expected_intent)
    print('Actual intent :', actual_intent)

def test_none_intent():
    test_request = "What time is it ?"
    test_response = client_runtime.prediction.resolve(CONFIG.LUIS_APP_ID, query=test_request)
    expected_intent = "none"
    actual_intent = test_response.top_scoring_intent.intent

    print('Test None intent :')
    print('-'*22)
    assert actual_intent == expected_intent
    print('Query :', test_request)
    print('Expected intent :', expected_intent)
    print('Actual intent :', actual_intent)

def test_order_travel_intent():
    test_request = "I need to book a flight"
    test_response = client_runtime.prediction.resolve(CONFIG.LUIS_APP_ID, query=test_request)
    expected_intent = "bookFlight"
    actual_intent = test_response.top_scoring_intent.intent

    print('Test Booking intent :')
    print('-'*22)
    assert actual_intent == expected_intent
    print('Query :', test_request)
    print('Expected intent :', expected_intent)
    print('Actual intent :', actual_intent)

def search_entity_type():
    test_request = "I would like to book a travel from Washington to Caprica from 15-08-2023 to 15-09-2023 for a budget of 100 dollars"
    test_response = client_runtime.prediction.resolve(CONFIG.LUIS_APP_ID, query=test_request)
    print('Result entities for :')
    print(test_request)
    for i in range(len(test_response.entities)):
        print(f' Entity {i}:', test_response.entities[i].type)
        
def test_order_travel_intent_origin_entity():
    test_request = "I need a trip from Washington"
    test_response = client_runtime.prediction.resolve(CONFIG.LUIS_APP_ID, query=test_request)
    expected_origin = "washington"
    actual_origin = ""
    if test_response.entities[0].type == 'or_city':
        actual_origin = test_response.entities[0].entity
    
    print('Test Origin entity :')
    print('-'*22)
    assert actual_origin == expected_origin
    print('Query :', test_request)
    print('Expected origin :', expected_origin)
    print('Actual origin :', actual_origin)    

def test_order_travel_intent_destination_entity():
    test_request = "I'd like to go to Caprica"
    test_response = client_runtime.prediction.resolve(CONFIG.LUIS_APP_ID, query=test_request)
    expected_destination = "caprica"
    actual_destination = ""
    if test_response.entities[0].type == 'dst_city':
        actual_destination = test_response.entities[0].entity

    print('Test Destination entity :')
    print('-'*22)
    assert actual_destination == expected_destination
    print('Query :', test_request)
    print('Expected destination :', expected_destination)
    print('Actual destination :', actual_destination) 

def search_entity_type_date():
    test_request = "I would like to book a travel from 15-08-2023 to 15-09-2023"
    test_response = client_runtime.prediction.resolve(CONFIG.LUIS_APP_ID, query=test_request)
    print('Result entities for :')
    print(test_request)
    for i in range(len(test_response.entities)):
        print(f' Entity {i}:', test_response.entities[i].type)

def test_order_travel_intent_travel_dates_entity():
    test_request = "I would like to book a travel from 15-08-2023 to 15-09-2023"
    test_response = client_runtime.prediction.resolve(CONFIG.LUIS_APP_ID, query=test_request)

    expected_start_travel_date = "15-08-2023"
    actual_start_travel_date = ""
    #print('Respone :', test_response)

    print('Test Dates entities :')
    print('-'*22)
    if test_response.entities[0].type == 'str_date':
        actual_start_travel_date = test_response.entities[1].entity
        print('actual_start_travel_date :', actual_start_travel_date)
    if not actual_start_travel_date == expected_start_travel_date :
        print(' '*15+'WARNING')
    print('Query :', test_request)
    print('Expected start_travel_date :', expected_start_travel_date)
    print('Actual start_travel_date :', actual_start_travel_date) 

    expected_end_travel_date = "15-09-2023"
    actual_end_travel_date = ""
    if test_response.entities[0].type == 'end_date':
        actual_end_travel_date = test_response.entities[0].entity

    if not actual_end_travel_date == expected_end_travel_date :
        print(' '*15+'WARNING')    
    print('Expected end_travel_date :', expected_end_travel_date)
    print('Actual end_travel_date :', actual_end_travel_date)

def test_order_travel_intent_budget_entity():
    test_request = "Need to book a trip for a budget of 100 dollars"
    test_response = client_runtime.prediction.resolve(CONFIG.LUIS_APP_ID, query=test_request)
    expected_budget = "100"
    actual_budget = ""
    if test_response.entities[0].type == 'budget':
        actual_budget = test_response.entities[0].entity

    print('Test Budget entity :')
    print('-'*22)
    assert actual_budget == expected_budget
    print('Query :', test_request)
    print('Expected budget :', expected_budget)
    print('Actual budget :', actual_budget)


# =====================================================
print('='*35)
print('Intents :')
print('='*35)
test_greetings_intent()
print('='*25)
test_none_intent()
print('='*25)
test_order_travel_intent()
print('')

print('='*35)
search_entity_type()
print('='*35)
test_order_travel_intent_origin_entity()
print('='*25)
test_order_travel_intent_destination_entity()
print('='*25)
search_entity_type_date()
print('-'*22)
test_order_travel_intent_travel_dates_entity()
print('='*25)
test_order_travel_intent_budget_entity()