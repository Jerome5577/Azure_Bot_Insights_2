
import requests, json
from sklearn.metrics import precision_recall_fscore_support

from config import app_id, subscription_key, predictionKey, predictionEndpoint, slot_name

# =====================================================================
# Authenticate prediction runtime client ------------------------------
# =====================================================================
#app_id = ""
#subscription_key = ""
# Prediction
#predictionKey = ''
#predictionEndpoint = ''
#slot_name = ''

class performance_evaluator():
    """
    Evaluate Luis model performances for intents and entities predictions VS ground truth.
    """

    def __init__(self, ground_truth):
        """
        Input :
            ground_truth (dict) : base list with the utterances and the entities
            {
                    "text": "Hi I'd like to go to Caprica from Busan, between Sunday August 21, 2016 and Wednesday August 31, 2016",
                    "intentName": "bookFlight",
                    "entityLabels": [
                        {
                            "startCharIndex": 21,
                            "endCharIndex": 28,
                            "entityName": "dst_city"
                        },
                        {
                            "startCharIndex": 34,
                            "endCharIndex": 39,
                            "entityName": "or_city"
                        },
                        {
                            "startCharIndex": 49,
                            "endCharIndex": 71,
                            "entityName": "str_date"
                        },
                        {
                            "startCharIndex": 76,
                            "endCharIndex": 101,
                            "entityName": "end_date"
                        }
                    ]
                }
            entities_name (list of str) : list of the names of the predicted entities
        """
        self.ground_truth = ground_truth

    def __get_prediction(self, text):
        """
        Send a request to the Luis model to get the predictions of a given utterance
        Input :
            text (str) : utterance to predict
        Output :
            response.json() : json file containing the predictions
            =========================
            {'query': "Hi I'd like to go to Caprica from Busan, between Sunday August 21, 2016 and Wednesday August 31, 2016"}      
            (response.prediction.top_intent) Top intent: bookFlight 
            (response.prediction.intents) Intents: 
                    "bookFlight"
            (response.prediction.entities) Entities: {'dst_city': ['Caprica'], 'or_city': ['Busan,'], 'datetimeV2': [{'type': 'daterange', 'values': [{'timex': '(2016-08-21,2016-08-31,P10D)', 'resolution': [{'start': '2016-08-21', 'end': '2016-08-31'}]}]}], 'str_date': ['Sunday August 21, 2016'], 'number': [21, 2016, 31, 2016], 'end_date': ['Wednesday August 31, 2016']}
            =========================
        """
        # Example Query : 
        # predictionEndpoint/luis/prediction/v3.0/apps/app_id/slots/production/predict?verbose=true&show-all-intents=true&log=true&subscription-key=subscription_key&query=YOUR_QUERY_HERE
        connexion_string = f"{predictionEndpoint}luis/prediction/v3.0/apps/{app_id}/slots/{slot_name}/predict"
        headers = {}
        params = {
                'query': text,
                'timezoneOffset': '0',
                'verbose': 'true',
                'show-all-intents': 'true',
                'spellCheck': 'false',
                'staging': 'false',
                'subscription-key': subscription_key
                }
        
        response = requests.get(connexion_string, headers=headers, params=params)
        return response.json()
    
    def evaluate_intents_performance(self):
        """
        Calculate intents prediction performance
        Output :
            precision (float)
            recall (float)
            f_score (float)
        """
        # Get true intents
        intents_true = []
        intents_pred = []

        # Calculate predicted intents
        for turn in self.ground_truth:
            text = turn["text"]
            
            response = self.__get_prediction(text)
            
            try: # there may be some instances where responce["predicion"] doesn't exist
                intent_pred = response["prediction"]["topIntent"]                
                '''
                # intentNames = 'bookFlight' + ["confirm", "greetings", "none"]
                if intent_pred == 'bookFlight' :
                    intent_pred = 1
                if intent_pred == 'confirm' :
                    intent_pred = 2
                if intent_pred == 'greetings' :
                    intent_pred = 3
                if intent_pred == 'none' :
                    intent_pred = 4
                '''                       
                intents_pred.append(intent_pred)
                # Keep intent_true evalauted after intent_pred to make sure that the 2 tables have the same length 
                intent_true = turn["intentName"]                
                '''
                if intent_true == 'bookFlight' :
                    intent_true = 1
                if intent_true == 'confirm' :
                    intent_true = 2
                if intent_true == 'greetings' :
                    intent_true = 3
                if intent_true == 'none' :
                    intent_true = 4
                '''    
                intents_true.append(intent_true)
            except KeyError:
                pass
            #print('Lenght pred ;', len(intents_pred), intents_pred)
            #print('Lenght true ;', len(intents_true), intents_true)
        precision, recall, fscore, _ = precision_recall_fscore_support(intents_true, intents_pred, average='micro')
        return precision, recall, fscore
    
def main():
    # Load data for evaluation
    evaluation_file_name = "./datas/test_dict.json"
    with open(evaluation_file_name, "r") as f:
        ground_truth = json.load(f)

    
    perf_ev = performance_evaluator(ground_truth)

    print("\n----------- performances evaluation -------------")
    print("Sample size : ", len(ground_truth))

    # Evaluate intents prediction performance
    precision, recall, fscore = perf_ev.evaluate_intents_performance()
    print("\nIntents performances")
    print("\tPrecision = {:.2f}".format(precision))
    #print("\tPrecision = :", round(precision ,2))
    print("\tRecall = {:.2f}".format(recall))
    print("\tF-score = {:.2f}".format(fscore))


if __name__ == "__main__":
    main()