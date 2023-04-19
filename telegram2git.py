
import pathlib
import utils

import telegram
import telegram.ext
import MessageSaver

def token_read(path):
    return utils.read_json(pathlib.Path(path)).get('token')


async def start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=telegram.ForceReply(selective=True),
    )


async def help_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def echo(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        print('\t', 'update.message: ', update.message)
        await update.message.reply_text(update.message.text)

    if update.channel_post:
        MessageSaver.MessageSaverTELCON(update)


def run(token: str) -> None:
    application = telegram.ext.ApplicationBuilder().token(token).build()

    application.add_handler(telegram.ext.CommandHandler("start", start))
    application.add_handler(telegram.ext.CommandHandler("help", help_command))

    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.ALL, echo))

    application.run_polling()

