from aiounittest.case import AsyncTestCase
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from bot_config import DefaultConfig

class LuisRecognizerTest(AsyncTestCase):
    CONFIG = DefaultConfig()
    _luisAppId: str = CONFIG.LUIS_APP_ID
    _subscriptionKey: str = CONFIG.LUIS_API_KEY
    _endpoint: str = CONFIG.LUIS_API_HOST_NAME

    async def test_multiple_intents_list_entity_with_single_value(self):
        utterance: str = "I need to book a flight from Atlanta to Toronto on april 12th and to april 21st. I have a budget of 2100$."

        client = LUISRuntimeClient(LuisRecognizerTest._endpoint, 
                                   CognitiveServicesCredentials(LuisRecognizerTest._subscriptionKey))
        
        result = client.prediction.resolve(LuisRecognizerTest._luisAppId, query=utterance)
        print('Result entities  :')
        for i in range(len(result.entities)):
            print(f' Entity {i}:', result.entities[i].type)
        print()    
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.query)
        self.assertEqual(utterance, result.query)
        self.assertIsNotNone(result.top_scoring_intent.intent)
        self.assertEqual("bookFlight", result.top_scoring_intent.intent)
        self.assertIsNotNone(result.entities)
        self.assertEqual("budget", result.entities[0].type)
        self.assertEqual("2100 $ .", result.entities[0].entity)
        self.assertEqual("dst_city", result.entities[1].type)
        self.assertEqual("toronto", result.entities[1].entity)
        self.assertEqual("end_date", result.entities[2].type)
        self.assertEqual("april 21st .", result.entities[2].entity)
        self.assertEqual("or_city", result.entities[3].type)
        self.assertEqual("atlanta", result.entities[3].entity)
        self.assertEqual("str_date", result.entities[4].type)
        self.assertEqual("april 12th", result.entities[4].entity)
        

        