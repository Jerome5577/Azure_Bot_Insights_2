# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.core.bot_telemetry_client import Severity

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.schema import InputHints
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient

from .cancel_and_help_dialog import CancelAndHelpDialog

from .start_date_resolver_dialog import StartDateResolverDialog
from .end_date_resolver_dialog import EndDateResolverDialog


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
        self.add_dialog(StartDateResolverDialog(StartDateResolverDialog.__name__, self.telemetry_client))
        self.add_dialog(EndDateResolverDialog(EndDateResolverDialog.__name__, self.telemetry_client))  

        #Python dictionary used to save chat history
        self.chat_history = dict()
    
    # ==== Origine ==== # 
    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        self.chat_history["chat_request"] = step_context._turn_context.activity.text

        booking_details = step_context.options
        print('booking_details : ', booking_details)

        if booking_details.origin is None:
            msg = "What is the name of the city you would you like to leave from?"
            prompt_message = MessageFactory.text(msg, msg, InputHints.expecting_input)
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.origin)
        
    
    # ==== Destination ==== # 
    async def destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for destination city."""
        self.chat_history["chat_request"] = step_context._turn_context.activity.text

        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.origin = step_context.result
        print('booking_details.origin : ', booking_details.origin)
        if booking_details.destination is None:
            msg = "What is the name of the city you would you like to go?"
            prompt_message = MessageFactory.text(msg, msg, InputHints.expecting_input)
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.destination)

    
    # ==== Start Date ==== # 
    async def start_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for departure date.
        This will use the DATE_RESOLVER_DIALOG."""
        self.chat_history["chat_request"] = step_context._turn_context.activity.text

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
        self.chat_history["chat_request"] = step_context._turn_context.activity.text

        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.start_date = step_context.result

        if not booking_details.end_date or self.is_ambiguous(booking_details.end_date):
            return await step_context.begin_dialog(EndDateResolverDialog.__name__, booking_details.end_date)  # pylint: disable=line-too-long

        return await step_context.next(booking_details.end_date)
    

    # ==== Budget ==== # 
    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for budget."""
        self.chat_history["chat_request"] = step_context._turn_context.activity.text

        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.end_date = step_context.result

        if booking_details.budget is None:
            msg = "I didn;t notice information for the budget, can you tell me ?"
            prompt_message = MessageFactory.text(msg, msg, InputHints.expecting_input)
            return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.budget)


    # ==== Confirm ==== # 
    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        self.chat_history["chat_request"] = step_context._turn_context.activity.text

        booking_details = step_context.options

        # Capture the results of the previous step's prompt
        booking_details.budget = step_context.result
        
        msg = (
            f"Please confirm, your travel from : { booking_details.origin } to: { booking_details.destination }"
            f" depature date on : { booking_details.start_date } to the: { booking_details.end_date}"
            f" and for a budget of : { booking_details.budget }."
        )

        # YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )
    
    # ==== Final ==== #
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction, track data, and end the dialog."""
        self.chat_history["chat_request"] = step_context._turn_context.activity.text

        # Create data to track in App Insights
        booking_details = step_context.options

        properties = {}
        properties["origin"] = booking_details.origin
        properties["destination"] = booking_details.destination
        properties["departure_date"] = booking_details.start_date
        properties["return_date"] = booking_details.end_date
        properties["budget"] = booking_details.budget
        
        # If OK
        if step_context.result:
            # Track YES data
            self.telemetry_client.track_trace("YES answer", properties,"VALID")
            self.telemetry_client.track_trace("CHAT_HISTORY_VALID", self.chat_history, "VALID")
            return await step_context.end_dialog(booking_details)
        
        # If Not OK
        else:
            sorry_msg = "Sorry for not answering your wishes."
            prompt_sorry_msg = MessageFactory.text(sorry_msg, sorry_msg, InputHints.ignoring_input)

            self.telemetry_client.track_trace("NO answer", properties, "ERROR")
            self.telemetry_client.track_trace("CHAT_HISTORY_ERROR", self.chat_history, "ERROR")

            await step_context.context.send_activity(prompt_sorry_msg)

        return await step_context.end_dialog()

    
    # ==== Ambiguous date ==== #
    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
