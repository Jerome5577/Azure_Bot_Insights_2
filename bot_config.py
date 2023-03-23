#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Bot Configuration"""

    ############## Azure Bot Service ###############
    PORT = 3978
    #APP_ID = os.environ.get("MicrosoftAppId", "") # 
    #APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "") #  
    ## Azure
    APP_ID = os.environ.get("MicrosoftAppId", "f7974c82-d897-4ea6-a5f2-f7b2cefe2889") #V5
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "Ge58Q~GdgHK6k0AF8X9c1lU3ICJzvXQyfap1ac3p") #V5

    ############## LUIS Service ###############
    ##### V2
    LUIS_APP_ID = os.environ.get("LuisAppId", "26eb04e6-67da-4c77-8c4f-46d9bb6635dc")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "a4983a29ae8348d1a71442db579c51bd")
    
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com" (<your region>.api.cognitive.microsoft.com)
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "https://luis-app-predicition.cognitiveservices.azure.com/")
    
    ############## App Insights Service ###############
    # Insights
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "0d915ba4-8f0b-437c-a4a9-41807101e124"
    ) #V5


    
