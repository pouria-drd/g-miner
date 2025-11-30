from logging import Logger
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler

from ..tools import protect


class GeneralHandlers:
    """
    Handles general user interactions like /start, /help, and echoing.
    """

    def __init__(self, logger: Logger):
        self.logger = logger

    @protect
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /start command.
        """
        # Extract the user and name from the update
        user = update.effective_user
        name = user.name  # type: ignore

        # Log the event
        self.logger.info(f"Handler Triggered: /start by {name}")

        await update.message.reply_text(  # type: ignore
            f"Greetings, {name}. System operational.",
            reply_to_message_id=update.message.message_id,  # type: ignore
        )

    def register(self, app: Application):
        """
        Attaches these handlers to the main application.
        """
        app.add_handler(CommandHandler("start", self.start))
        self.logger.info("GeneralHandlers registered successfully.")
