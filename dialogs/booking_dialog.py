# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

from datatypes_date_time.timex import Timex

# from botbuilder.core.bot_telemetry_client import Severity

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.schema import InputHints
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from bot_config import DefaultConfig
from .cancel_and_help_dialog import CancelAndHelpDialog

from .start_date_resolver_dialog import StartDateResolverDialog
from .end_date_resolver_dialog import EndDateResolverDialog

CONFIG = DefaultConfig()
# INSTRUMENTATION_KEY = CONFIG.APPINSIGHTS_INSTRUMENTATION_KEY
# AppInsights Logger
# name = __name__
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=0d915ba4-8f0b-437c-a4a9-41807101e124')
)


class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    # ==== Initialization === #
    def __init__(
            self,
            dialog_id: str = None,
            telemetry_client: BotTelemetryClient = NullTelemetryClient()):

        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client)
        self.telemetry_client = telemetry_client

        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client
        self.add_dialog(text_prompt)

        # Correct Waterfall Dialog with the 5 requested entities
        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.origin_step,
                self.destination_step,
                self.start_date_step,
                self.end_date_step,
                self.budget_step,
                self.confirm_step,
                self.final_step,
            ])
        waterfall_dialog.telemetry_client = telemetry_client
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(StartDateResolverDialog(
            StartDateResolverDialog.__name__, self.telemetry_client))
        self.add_dialog(EndDateResolverDialog(
            EndDateResolverDialog.__name__, self.telemetry_client))

        # Python dictionary used to save chat history
        self.chat_history = dict()

    # ==== Origine ==== #
    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        self.chat_history["chat_initial_request"] = step_context.context.activity.text

        booking_details = step_context.options
        print('booking_details : ', booking_details)

        if booking_details.origin is None:
            msg = "What is the name of the city you would you like to leave from?"
            prompt_message = MessageFactory.text(
                msg, msg, InputHints.expecting_input)
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.origin)

    # ==== Destination ==== #

    async def destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for destination city."""
        self.chat_history["chat_origin"] = step_context.context.activity.text

        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.origin = step_context.result
        print('booking_details.origin : ', booking_details.origin)
        if booking_details.destination is None:
            msg = "What is the name of the city you would you like to go?"
            prompt_message = MessageFactory.text(
                msg, msg, InputHints.expecting_input)
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.destination)

    # ==== Start Date ==== #

    async def start_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for departure date.
        This will use the DATE_RESOLVER_DIALOG."""
        self.chat_history["chat_destination"] = step_context.context.activity.text
        
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        print('start date : ', booking_details.start_date)
        if booking_details.start_date is None or self.is_ambiguous(booking_details.start_date):
            return await step_context.begin_dialog(StartDateResolverDialog.__name__, booking_details.start_date)  # pylint: disable=line-too-long

        return await step_context.next(booking_details.start_date)

    # ==== End Date ==== #

    async def end_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for departure date.
        This will use the DATE_RESOLVER_DIALOG."""
        self.chat_history["chat_departure_date"] = step_context.context.activity.text

        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.start_date = step_context.result

        if not booking_details.end_date or self.is_ambiguous(booking_details.end_date):
            return await step_context.begin_dialog(EndDateResolverDialog.__name__, booking_details.end_date)  # pylint: disable=line-too-long

        return await step_context.next(booking_details.end_date)

    # ==== Budget ==== #

    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for budget."""
        self.chat_history["chat_end_date"] = step_context.context.activity.text
        

        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.end_date = step_context.result

        if booking_details.budget is None:
            msg = "I didn't notice information for the budget, can you tell me ?"
            prompt_message = MessageFactory.text(
                msg, msg, InputHints.expecting_input)
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.budget)

    # ==== Confirm ==== #

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        self.chat_history["chat_budget"] = step_context.context.activity.text

        booking_details = step_context.options
        # Capture the results of the previous step's prompt
        booking_details.budget = step_context.result
        msg = (
            f"Please confirm, your travel from : { booking_details.origin } to: { booking_details.destination }"
            f" depature date on : { booking_details.start_date } to the: { booking_details.end_date}"
            f" and for a budget of : { booking_details.budget }.")
        prompt_message = MessageFactory.text(
            msg, msg, InputHints.expecting_input)
        return await step_context.prompt(ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message))

    # ==== Final ==== #
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction, track data, and end the dialog."""
        self.chat_history["chat_confirm"] = step_context.context.activity.text

        # Create data to track in App Insights
        booking_details = step_context.options
        properties = {}
        properties["chat_initial_request"] = self.chat_history["chat_initial_request"]
        properties["origin"] = booking_details.origin
        properties["destination"] = booking_details.destination
        properties["departure_date"] = booking_details.start_date
        properties["return_date"] = booking_details.end_date
        properties["budget"] = booking_details.budget
        # If OK
        if step_context.result:
            # Track YES data
            #self.telemetry_client.track_trace("telemetry_YES answer", properties, "telemetry_VALID")
            #self.telemetry_client.track_trace("telemetry_CHAT_HISTORY_VALID", self.chat_history, "telemetry_CHAT_HISTORY_VALID")
            # Use properties in logging statements
            #logger.warning('opencensus_logger_VALID', extra=properties)
            #logger.warning('opencensus_logger_CHAT_HISTORY_VALID', extra=self.chat_history)
            return await step_context.end_dialog(booking_details)
        # If Not OK
        else:
            sorry_msg = "Sorry for not helping you"
            prompt_sorry_msg = MessageFactory.text(sorry_msg, sorry_msg, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_sorry_msg)
            #self.telemetry_client.track_trace("telemetry_NO answer", properties, "telemetry_ERROR")
            #self.telemetry_client.track_trace("telemetry_CHAT_HISTORY_ERROR", properties, "telemetry_CHAT_HISTORY_ERROR")
            # Use properties in logging statements
            #logger.warning('opencensus_logger_ERROR', extra=self.chat_history)
            #logger.warning('opencensus_logger_CHAT_HISTORY_ERROR', extra=properties )
            logger.error(properties)

            return await step_context.end_dialog(None)

    # ==== Ambiguous date ==== #

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
