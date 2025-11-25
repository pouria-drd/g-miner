from telegram import Update
from telegram.ext import ContextTypes
from modules.configs import ADMIN_CHAT_IDS


def protected(func):
    """
    Decorator to allow only specific users to execute a handler.
    Replies with a warning if unauthorized.
    """

    async def wrapped(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = update.effective_user

        if not user or str(user.id) not in ADMIN_CHAT_IDS:
            if update.message:
                await update.message.reply_text(
                    "⛔ You are not allowed to use this bot."
                )
            return  # Stop execution for unauthorized users
        return await func(self, update, context, *args, **kwargs)

    return wrapped
