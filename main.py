#!/usr/bin/python
import argparse
import os
from urllib.parse import urlparse

import git
import telegram
import telegram.ext

import pathlib
import textwrap
from string import Template
import slugify
from telegram.ext import ContextTypes

import utils

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename='telegram-to-git-connector.log',
)
#logger = logging.getLogger(__name__)


TEMPLATE_REPO_CHAT_DIRNAME = Template('chat-$id-$title')
TEMPLATE_REPO_POST_FILENAME = Template('post-$id-$text.txt')
SAVE_RAW_DATA_CHANNEL_POST = True

REPO_PATH = 'some-tgbot-data'


global_git_repo_dir = 'GIT-REPO-DIR'


def add_file_commit_and_push_repo(repo_dir, file_path):
    repo = git.Repo(pathlib.Path(repo_dir).absolute().as_posix())
    file = pathlib.Path(file_path)
    repo.index.add([file.as_posix()])

    comment = f'Add {file.name} at {utils.datetime_now()}'
    repo.index.commit(comment)
    repo.remote('origin').push()


def clone_repo(git_url, place=pathlib.Path()):
    last_per_git_url = urlparse(git_url).path.strip('/').split('/')[-1].__str__()
    git_dirname = 'git-repo-dirname'
    if last_per_git_url.endswith('.git'):
        git_dirname = last_per_git_url.replace('.git', '')

    git_repo_dir = pathlib.Path(place).joinpath(git_dirname)

    try:
        git.Repo.clone_from(git_url, git_repo_dir)

    except Exception as e:
        print('Error Clone Git Repo!', 'Error', e)
        logging.warning('🟠 Warning. Clone Git Repo!'+ str(e))

    if not git_repo_dir.exists():
        print('🔴, Error!'+ 'No Git Repo Dir')
        logging.error('🔴, Error!'+ 'No Git Repo Dir')
        return False

    return git_repo_dir.as_posix()


def save_channel_post(channel_post, git_repo_dir: str | pathlib.Path):
    logging.info('🟢 Save post ID'+channel_post.message_id.__str__())
    print('🟢 Save post ID' + channel_post.message_id.__str__())
    output_data = {}

    post_text = channel_post.text_markdown_v2.__str__().replace("\\", "")
    output_data['text'] = f'\n{post_text}\n'

    output_data['date'] = channel_post.date.__str__()
    output_data['message_id'] = channel_post.message_id.__str__()

    if SAVE_RAW_DATA_CHANNEL_POST:
        output_data['rawdata'] = channel_post

    chat_id = channel_post.chat.id.__str__()
    if chat_id.startswith('-100'):
        chat_id = chat_id.removeprefix('-100')
    chat_title = textwrap.shorten(slugify.slugify(channel_post.chat.title.__str__()), width=64, placeholder='')

    repo_chat_dirname = TEMPLATE_REPO_CHAT_DIRNAME.substitute(id=chat_id, title=chat_title)
    repo_chat_dir = pathlib.Path(git_repo_dir).joinpath(repo_chat_dirname)
    repo_chat_dir.mkdir(parents=True, exist_ok=True)

    post_id = channel_post.message_id.__str__()
    post_text = str(textwrap.shorten(slugify.slugify(channel_post.text.__str__()), width=64, placeholder=''))

    repo_post_filename = TEMPLATE_REPO_POST_FILENAME.substitute(id=post_id, text=post_text)
    repo_post_file = repo_chat_dir.joinpath(repo_post_filename)

    utils.write_yaml(repo_post_file, output_data)

    relative_post_file = repo_post_file.relative_to(global_git_repo_dir)
    add_file_commit_and_push_repo(global_git_repo_dir, relative_post_file)


async def start(update: telegram.Update) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=telegram.ForceReply(selective=True),
    )


async def help_command(update: telegram.Update) -> None:
    await update.message.reply_text("Help!")


async def echo(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        print('\t', 'update.message: ', update.message)
        await update.message.reply_text(update.message.text)

    if update.channel_post:
        print('update.channel_post')
        try:
            save_channel_post(update.channel_post, global_git_repo_dir)

        except Exception as e:
            print('🔴', 'Error in Save', 'Make log')
            logging.error('🔴 Error in Save' + 'Make log')
            print('🦄' + 'ID: ' + str(update.channel_post.message_id) + str(e))
            logging.error('🦄'+ 'ID: ' + str(update.channel_post.message_id) + str(e))
            print(e)


def run(telegram_token: str) -> None:
    print('🟢 Running Normal....')

    logging.info('🟢 Running Normal....')

    logging.critical('🟣 CRITICAL')
    logging.error('🔴 ERROR')
    logging.warning('🟠 WARNING')
    logging.info('🟢 INFO')
    logging.debug('🔵 DEBUG')

    application = telegram.ext.ApplicationBuilder().token(telegram_token).build()

    application.add_handler(telegram.ext.CommandHandler("start", start))
    application.add_handler(telegram.ext.CommandHandler("help", help_command))

    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.ALL, echo))

    application.run_polling()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Telegram to Git (telegram2git).')

    parser.add_argument('--token_json_path', dest='token_path',
                        type=str,
                        required=True,
                        help='Telegram token set')

    parser.add_argument('--git_url_json_path', dest='git_url_path',
                        type=str,
                        required=True,
                        help='Remote git url to store set')

    parser.add_argument('--repo-place', dest='repo_place',
                        type=str,
                        required=False,
                        help='Repo Parent dir place local to store set')

    args = parser.parse_args()

    token_path = os.path.expanduser(args.token_path)
    token = utils.read_json(pathlib.Path(token_path)).get('token')
    if not token:
        print('Error', 'No token')
        exit()

    git_url_path = os.path.expanduser(args.git_url_path)
    git_url_real = utils.read_json(pathlib.Path(git_url_path)).get('url')

    if not git_url_real:
        print('Error', 'No git_url')
        exit()

    print('token', token)
    print('git_url', git_url_real)

    repo_place = '.'
    if args.repo_place:
        repo_place = os.path.expanduser(args.repo_place)
    print('repo_place', f'<{repo_place}>')

    global_git_repo_dir = clone_repo(git_url=git_url_real, place=repo_place)
    if not global_git_repo_dir:
        print('Error Dir Path', 'Exit')
        exit()

    run(token)
