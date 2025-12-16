from logging import Logger
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler

from ..wrappers import admin_only


class GeneralHandlers:
    """
    Handles general user interactions like /start, /help, and echoing.
    """

    def __init__(self, logger: Logger):
        self.logger = logger

    @admin_only
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /start command.
        """
        user = update.effective_user
        name = user.name  # type: ignore

        self.logger.info(f"Handler Triggered: /start by {name}")

        message = (
            f"👋 <b>Greetings, {name}!</b>\n\n"
            "🤖 System operational.\n\n"
            "<b>Available Commands:</b>\n"
            "• /start - Show this message\n"
            "• /settings - Manage bot settings\n"
            "• /help - Get help information\n"
            "• /status - Check system status"
        )

        await update.message.reply_text(  # type: ignore
            message,
            parse_mode="HTML",
            reply_to_message_id=update.message.message_id,  # type: ignore
        )

    @admin_only
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /help command.
        """
        user = update.effective_user
        self.logger.info(f"Handler Triggered: /help by {user.name}")  # type: ignore

        message = (
            "📖 <b>Help Information</b>\n\n"
            "<b>Settings Management:</b>\n"
            "• /status - Check system status\n"
            "• /settings - Open settings menu\n"
            "• /reload - Reload settings from .env file\n\n"
            "<b>What you can configure:</b>\n"
            "• 🕒 Scheduler settings (timing, intervals)\n"
            "• 💰 Zarbaha scraper settings (rates, timeouts)\n\n"
            "<b>How to edit:</b>\n"
            "1. Use /settings to open the menu\n"
            "2. Select a category\n"
            "3. Choose a setting to edit\n"
            "4. Send the new value\n\n"
            "All changes are saved to the .env file automatically."
        )

        await update.message.reply_text(  # type: ignore
            message,
            parse_mode="HTML",
            reply_to_message_id=update.message.message_id,  # type: ignore
        )

    @admin_only
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /status command - shows system status.
        """
        from modules.configs import get_settings

        user = update.effective_user
        self.logger.info(f"Handler Triggered: /status by {user.name}")  # type: ignore

        settings = get_settings()

        status_icon = "✅" if settings["SCHEDULER_ENABLED"] else "⏸️"

        message = (
            f"{status_icon} <b>System Status</b>\n\n"
            f"<b>Scheduler:</b> {'Enabled' if settings['SCHEDULER_ENABLED'] else 'Disabled'}\n"
            f"<b>Interval:</b> {settings['SCHEDULER_INTERVAL_MINUTES']} minutes\n"
            f"<b>Timezone:</b> {settings['SCHEDULER_TIME_ZONE']}\n"
            f"<b>Active Window:</b> {settings['SCHEDULER_START_TIME']} - {settings['SCHEDULER_END_TIME']}\n\n"
            f"<b>Channel:</b> {settings['TELEGRAM_CHANNEL_ID']}\n"
            f"<b>Admins:</b> {len(settings['ADMIN_CHAT_IDS'])}\n\n"
            f"Use /settings to modify configuration."
        )

        await update.message.reply_text(  # type: ignore
            message,
            parse_mode="HTML",
            reply_to_message_id=update.message.message_id,  # type: ignore
        )

    def register(self, app: Application):
        """
        Attaches these handlers to the main application.
        """
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("status", self.status_command))
        self.logger.info("GeneralHandlers registered successfully.")
