
import sys
import os
import pathlib
app_dir = pathlib.Path(__file__).parent.parent
print('app_dir :',app_dir)
sys.path.append(str(app_dir)) # add bot module to system path if operated from its own working directory else import will fail
# ==========
# Récupérer le chemin absolu du dossier parent
parent_dir = os.path.dirname(os.path.abspath(__file__))  # le chemin absolu du fichier actuel
print('parent_dir :', parent_dir)
grandparent_dir = os.path.dirname(parent_dir)  # le chemin absolu du dossier parent
print('grandparent_dir :', grandparent_dir)
# Ajouter le chemin absolu du dossier parent à la liste des chemins de recherche de Python
sys.path.append(grandparent_dir)

# ==========
from bot_config import DefaultConfig
import logging
from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Request, Response, json_response

from botbuilder.core import (
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TelemetryLoggerMiddleware,
    UserState)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity
from botbuilder.applicationinsights import ApplicationInsightsTelemetryClient
from botbuilder.integration.applicationinsights.aiohttp import (
    AiohttpTelemetryProcessor,
    bot_telemetry_middleware)

from opencensus.ext.azure.log_exporter import AzureLogHandler
from adapter_with_error_handler import AdapterWithErrorHandler
from flight_booking_recognizer import FlightBookingRecognizer

from dialogs import MainDialog, BookingDialog
from bots import DialogAndWelcomeBot

from botbuilder.core.adapters import TestAdapter, TestFlow

CONFIG = DefaultConfig()

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)

# Create MemoryStorage, UserState and ConversationState
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
ADAPTER = AdapterWithErrorHandler(SETTINGS, CONVERSATION_STATE)

# Create telemetry client.
# Note the small 'client_queue_size'.  This is for demonstration purposes.  Larger queue sizes
# result in fewer calls to ApplicationInsights, improving bot performance at the expense of
# less frequent updates.
INSTRUMENTATION_KEY = CONFIG.APPINSIGHTS_INSTRUMENTATION_KEY
TELEMETRY_CLIENT = ApplicationInsightsTelemetryClient(
    INSTRUMENTATION_KEY, telemetry_processor=AiohttpTelemetryProcessor(), client_queue_size=10)
# Code for enabling activity and personal information logging.
TELEMETRY_LOGGER_MIDDLEWARE = TelemetryLoggerMiddleware(
    telemetry_client=TELEMETRY_CLIENT, log_personal_information=True
)
ADAPTER.use(TELEMETRY_LOGGER_MIDDLEWARE)

# AppInsights Logger 
name = __name__
logger = logging.getLogger(name)
logger.addHandler(AzureLogHandler(
        connection_string='InstrumentationKey=0d915ba4-8f0b-437c-a4a9-41807101e124')
        )

# Create dialogs and Bot
RECOGNIZER = FlightBookingRecognizer(CONFIG)
BOOKING_DIALOG = BookingDialog()
DIALOG = MainDialog(RECOGNIZER, BOOKING_DIALOG, telemetry_client=TELEMETRY_CLIENT)
BOT = DialogAndWelcomeBot(CONVERSATION_STATE, USER_STATE, DIALOG, TELEMETRY_CLIENT)

import unittest
import aiounittest


class Test_Bot_Activities_Test1(aiounittest.AsyncTestCase):
    # Below async methods will send a simple message that clearly reflects one of modelled intents
    # Will pass if trained LUIS model runs and of course if bot conditional logic remains unchanged
    async def no_test_welcome_test(self):
        adapter = TestAdapter(BOT.on_turn)
        test_flow = TestFlow(None, adapter)
        tf_1 = await test_flow.send("Hi")
        await tf_1.assert_reply("Hi ! To help you I need the following informations for your travel : origin, destination dates and budget.")
        #await adapter.test("Hi", "Hi ! To help you I need the following informations for your travel : origin, destination dates and budget.")    

    async def no_test_rejection_test(self):
        adapter = TestAdapter(BOT.on_turn)
        test_flow = TestFlow(None, adapter)
        tf_1 = await test_flow.send("Test")
        await tf_1.assert_reply("Sorry, I didn’t get that. Please try asking in a different way")
        #await adapter.test("Test", "Sorry, I didn’t get that. Please try asking in a different way")

    async def no_test_sipmle_element_start_(self):
        adapter = TestAdapter(BOT.on_turn)
        test_flow = TestFlow(None, adapter)
        tf_1 = await test_flow.send("Toronto to Washington")
        await tf_1.assert_reply("Could you give me a date of departure?")
        #await adapter.test("Toronto to Washington", "Could you give me a date of departure?")

    async def no_test_cancel_test(self):
        adapter = TestAdapter(BOT.on_turn)
        await adapter.test("Cancel", "Cancelling")
    
class Test_Bot_Activities_Test2(aiounittest.AsyncTestCase):
        # Below method will test a full conversation based on sentences containing most basic 
    # context elements. This dialog is known to work as soon as model is trained, 
    # hence expected replies will not change unless model or conversational logic change as well. 
    async def test_full_dialog_2_test(self):
        adapter = TestAdapter(BOT.on_turn)
        test_flow = TestFlow(None, adapter)
        tf_0 = await test_flow.send("Hello !")
        tf_1 = await tf_0.assert_reply("Hi ! To help you I need the following informations for your travel : origin, destination dates and budget.")
        tf_2 = await tf_1.send("I want to go from Paris to Seattle please!")
        tf_3 = await tf_2.assert_reply("Could you give me a date of departure?")
        tf_4 = await tf_3.send("22/08/2023")
        tf_5 = await tf_4.assert_reply("And when would you like to return?")
        tf_6 = await tf_5.send("28/08/2023")
        tf_7 = await tf_6.assert_reply("I didn;t notice information for the budget, can you tell me ?")
        tf_8 = await tf_7.send("200 dollars")
        await tf_8.assert_reply("Please confirm, your travel from : Paris to: Seattle depature date on : 2023-08-22 to the: 2023-08-28 and for a budget of : 200 dollars. (1) Yes or (2) No")
    
class Test_Bot_Activities_Test3(aiounittest.AsyncTestCase):
    async def test_full_dialog_3_test(self):
        adapter = TestAdapter(BOT.on_turn)
        test_flow = TestFlow(None, adapter)
        tf_0 = await test_flow.send("Hello !")
        tf_1 = await tf_0.assert_reply("Hi ! To help you I need the following informations for your travel : origin, destination dates and budget.")
        tf_2 = await tf_1.send("toronto to whashington from 18/12/23 to 26/12/23 for 200 dollars")
        await tf_2.assert_reply("Please confirm, your travel from : Toronto to: Whashington depature date on : 2023-12-18 to the: 2023-12-26 and for a budget of : 200. (1) Yes or (2) No ")
    
class Test_Bot_Activities_Test4(aiounittest.AsyncTestCase):
    async def test_full_dialog_4_test(self):
        adapter = TestAdapter(BOT.on_turn)
        test_flow = TestFlow(None, adapter)
        tf_0 = await test_flow.send("Hello !")
        tf_1 = await tf_0.assert_reply("Hi ! To help you I need the following informations for your travel : origin, destination dates and budget.")
        tf_2 = await tf_1.send("toronto to whashington from 18/12/23 to 26/12/23 for 200 dollars")
        tf_3 = await tf_2.assert_reply("Please confirm, your travel from : Toronto to: Whashington depature date on : 2023-12-18 to the: 2023-12-26 and for a budget of : 200. (1) Yes or (2) No ")
        tf_4 = await tf_3.send("2")
        tf_5 = await tf_4.assert_reply("Sorry for not helping you")
        tf_6 = await tf_5.assert_reply("Can I do someting else for you?")
        tf_7 = await tf_6.send("I want to go from Paris to Seattle please!")
        tf_8 = await tf_7.assert_reply("Could you give me a date of departure?")
        tf_9 = await tf_8.send("22/08/2023")
        tf_10 = await tf_9.assert_reply("And when would you like to return?")
        tf_11 = await tf_10.send("28/08/2023")
        tf_12 = await tf_11.assert_reply("I didn't notice information for the budget, can you tell me ?")
        tf_13 = await tf_12.send("200 dollars")
        tf_14 = await tf_13.assert_reply("Please confirm, your travel from : Paris to: Seattle depature date on : 2023-08-22 to the: 2023-08-28 and for a budget of : 200 dollars. (1) Yes or (2) No")
        tf_15 = await tf_14.send("2")
        tf_16 = await tf_15.assert_reply("Sorry for not helping you")
        tf_17 = await tf_16.assert_reply("Can I do someting else for you?")
        tf_18 = await tf_17.send("toronto to washington")
        tf_19 = await tf_18.assert_reply("Could you give me a date of departure?")
        tf_20 = await tf_19.send("quit")
        await tf_20.send("Cancelling")



class Test_Bot_Activities_Test5(aiounittest.AsyncTestCase):
    async def test_full_dialog_5_test(self):
        adapter = TestAdapter(BOT.on_turn)
        test_flow = TestFlow(None, adapter)
        tf_0 = await test_flow.send("Hello !")
        tf_1 = await tf_0.assert_reply("Hi ! To help you I need the following informations for your travel : origin, destination dates and budget.")
        tf_2 = await tf_1.send("I want to go from Paris to Seattle please!")
        tf_3 = await tf_2.assert_reply("Could you give me a date of departure?")
        tf_4 = await tf_3.send("12 august")     
        tf_5 = await tf_4.assert_reply("I’m sorry, for best results, please enter your departure date including the day, month and year, e.g. 01 January 2023")
        tf_6 = await tf_5.send("12 august 2023")
        tf_7 = await tf_6.assert_reply("And when would you like to return?")
        tf_8 = await tf_7.send("18 august 2023")
        tf_9 = await tf_8.assert_reply("I didn;t notice information for the budget, can you tell me ?")
        tf_10 = await tf_9.send("200 dollars")
        await tf_10.assert_reply("Please confirm, your travel from : Paris to: Seattle depature date on : 2023-08-12 to the: 2023-08-18 and for a budget of : 200 dollars.")

