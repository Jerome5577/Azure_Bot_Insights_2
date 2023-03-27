
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


class Test_Bot_Activities_Test(aiounittest.AsyncTestCase):
    # Below async methods will send a simple message that clearly reflects one of modelled intents
    # Will pass if trained LUIS model runs and of course if bot conditional logic remains unchanged
    async def test_welcome_test(self):
        adapter = TestAdapter(BOT.on_turn)
        await adapter.test("Hi", "Hi ! To help you I need the following informations for your travel : origin, destination dates and budget.")    

    async def exec_test_rejection_test(self):
        adapter = TestAdapter(BOT.on_turn)
        await adapter.test("Test", "Sorry, I didn’t get that. Please try asking in a different way")

    async def test_sipmle_element_start_(self):
        adapter = TestAdapter(BOT.on_turn)
        await adapter.test("Toronto to Washington", "Could you give me a date of departure?")

    async def test_cancel_test(self):
        adapter = TestAdapter(BOT.on_turn)
        await adapter.test("Cancel", "Cancelling")
    
    # Below method will test a full conversation based on sentences containing most basic 
    # context elements. This dialog is known to work as soon as model is trained, 
    # hence expected replies will not change unless model or conversational logic change as well. 
    async def test_full_dialog_1_test(self):
        adapter = TestAdapter(BOT.on_turn)
        test_flow = TestFlow(None, adapter)
        tf_2 = await test_flow.send("Hello I want to go from Paris to Seattle please!")
        tf_3 = await tf_2.assert_reply("Could you give me a date of departure?")
        tf_4 = await tf_3.assert_reply("12 august")     
        tf_5 = await tf_4.send("I’m sorry, for best results, please enter your departure date including the day, month and year, e.g. 01 January 2023")
        tf_6 = await tf_5.assert_reply("12 august 2023")
        tf_7 = await tf_6.assert_reply("And when would you like to return?")
        tf_8 = await tf_7.send("18 august 2023")
        tf_9 = await tf_8.assert_reply("I didn;t notice information for the budget, can you tell me ?")
        tf_10 = await tf_9.send("200 dollars")
        await tf_10.assert_reply("Please confirm, your travel from : Paris to: Seattle depature date on : 2023-08-12 to the: 2023-08-18 and for a budget of : 200 dollars.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
