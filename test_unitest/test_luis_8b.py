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
    test_response = client_runtime.prediction.resolve(
        CONFIG.LUIS_APP_ID, query=test_request)

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
    test_response = client_runtime.prediction.resolve(
        CONFIG.LUIS_APP_ID, query=test_request)
    expected_intent = "none"
    actual_intent = test_response.top_scoring_intent.intent

    print('Test None intent :')
    print('-'*22)
    assert actual_intent == expected_intent
    print('Query :', test_request)
    print('Expected intent :', expected_intent)
    print('Actual intent :', actual_intent)

def test_booking_intent():
    test_request = "I need to book a flight"
    test_response = client_runtime.prediction.resolve(
        CONFIG.LUIS_APP_ID, query=test_request)
    expected_intent = "bookFlight"
    actual_intent = test_response.top_scoring_intent.intent

    print('Test Booking intent :')
    print('-'*22)
    assert actual_intent == expected_intent
    print('Query :', test_request)
    print('Expected intent :', expected_intent)
    print('Actual intent :', actual_intent)

def search_entity(all_entities, type=None):
    actual_entity_searched = ""
    for i in range(len(all_entities)):
        print(f' Entity {i}:', all_entities[i].type)
        if all_entities[i].type == type:
            actual_entity_searched = all_entities[i].entity
    return actual_entity_searched

def test_booking_intent_origin_entity():
    test_request = "I need a trip from Washington"
    test_response = client_runtime.prediction.resolve(
        CONFIG.LUIS_APP_ID, query=test_request)
    expected_origin = "washington"
    actual_entity = ""

    all_entities = test_response.entities
    actual_entity = search_entity(all_entities, type='or_city')

    print('Test Origin entity :')
    print('-'*22)
    print('Actual entity :', actual_entity)
    assert actual_entity == expected_origin
    print('Query :', test_request)
    print('Expected origin :', expected_origin)
    print('Actual origin :', actual_entity)

def test_booking_intent_destination_entity():
    test_request = "I'd like to go to Caprica"
    test_response = client_runtime.prediction.resolve(
        CONFIG.LUIS_APP_ID, query=test_request)
    expected_destination = "caprica"
    actual_destination = ""

    all_entities = test_response.entities
    actual_destination = search_entity(all_entities, type='dst_city')

    print('Test Destination entity :')
    print('-'*22)
    print('Actual entity :', actual_destination)
    assert actual_destination == expected_destination
    print('Query :', test_request)
    print('Expected destination :', expected_destination)
    print('Actual destination :', actual_destination)

def test_booking_intent_travel_dates_entity():
    test_request = "I would like to book a travel from 15-08-2023 to 15-09-2023"
    test_response = client_runtime.prediction.resolve(
        CONFIG.LUIS_APP_ID, query=test_request)

    expected_start_travel_date = "15-08-2023"
    actual_start_travel_date = ""
    all_entities = test_response.entities

    print('Test Dates entities :')
    print('-'*22)
    print('Query :', test_request)
    actual_start_travel_date = search_entity(all_entities, type='str_date')
    if not actual_start_travel_date == expected_start_travel_date:
        print(' '*15+'WARNING')
    
    print('Expected start_travel_date :', expected_start_travel_date)
    print('Actual start_travel_date :', actual_start_travel_date)

    expected_end_travel_date = "15-09-2023"
    actual_end_travel_date = ""
    actual_end_travel_date = search_entity(all_entities, type='end_date')
    if not actual_end_travel_date == expected_end_travel_date:
        print(' '*15+'WARNING')
    print('Expected end_travel_date :', expected_end_travel_date)
    print('Actual end_travel_date :', actual_end_travel_date)

def test_booking_intent_budget_entity():
    test_request = "Need to book a trip for a budget of 100 dollars"
    test_response = client_runtime.prediction.resolve(
        CONFIG.LUIS_APP_ID, query=test_request)
    expected_budget = "100"
    actual_budget = ""

    all_entities = test_response.entities
    actual_budget = search_entity(all_entities, type='budget')

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
test_booking_intent()
print('')

print('='*35)
print('Entities :')
print('='*35)
test_booking_intent_origin_entity()
print('='*25)
test_booking_intent_destination_entity()
print('='*25)
test_booking_intent_travel_dates_entity()
print('='*25)
test_booking_intent_budget_entity()
