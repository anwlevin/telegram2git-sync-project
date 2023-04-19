#!/usr/bin/python

import os

import telegram
import telegram.ext

import pathlib
import textwrap
from string import Template
import slugify
import utils

TEMPLATE_REPO_CHAT_DIRNAME = Template('$id-Chat-$title')
TEMPLATE_REPO_POST_FILENAME = Template('$id-Post-$text.txt')
SAVE_RAW_DATA_CHANNEL_POST = True

REPO_PATH = 'some-tgbot-data'


def save_channel_post(channel_post, repo_path=REPO_PATH):
    output_data = {}

    post_text = channel_post.text_markdown_v2.replace("\\", "")
    output_data['text'] = f'\n{post_text}\n'

    output_data['date'] = channel_post.date
    output_data['message_id'] = channel_post.message_id

    if SAVE_RAW_DATA_CHANNEL_POST:
        output_data['rawdata'] = channel_post

    chat_id = str(channel_post.chat.id)
    if chat_id.startswith('-100'):
        chat_id = chat_id.removeprefix('-100')
    chat_title = textwrap.shorten(slugify.slugify(channel_post.chat.title), width=64, placeholder='')

    repo_chat_dirname = TEMPLATE_REPO_CHAT_DIRNAME.substitute(id=chat_id, title=chat_title)
    repo_chat_dir = pathlib.Path(repo_path).joinpath(repo_chat_dirname)
    repo_chat_dir.mkdir(parents=True, exist_ok=True)

    post_id = channel_post.message_id
    post_text = textwrap.shorten(slugify.slugify(channel_post.text), width=64, placeholder='')

    repo_post_filename = TEMPLATE_REPO_POST_FILENAME.substitute(id=post_id, text=post_text)
    repo_post_file = repo_chat_dir.joinpath(repo_post_filename)

    print(repo_post_file)
    utils.write_yaml(repo_post_file, output_data)


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
        save_channel_post(update.channel_post)


def run(telegram_token: str) -> None:
    application = telegram.ext.ApplicationBuilder().token(telegram_token).build()

    application.add_handler(telegram.ext.CommandHandler("start", start))
    application.add_handler(telegram.ext.CommandHandler("help", help_command))

    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.ALL, echo))

    application.run_polling()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Telegram to Git (telegram2git).')

    parser.add_argument('--tokenpath', dest='tokenpath',
                        type=str,
                        required=True,
                        help='token set')
    args = parser.parse_args()

    token_path = os.path.expanduser(args.tokenpath)
    token = utils.read_json(pathlib.Path(token_path)).get('token')
    run(token)
